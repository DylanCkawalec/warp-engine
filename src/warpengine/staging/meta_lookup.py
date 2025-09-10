"""
Meta Lookup System - Intelligent code understanding and navigation
Provides mechanical understanding of the entire codebase structure.
"""

from __future__ import annotations
import ast
import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field

from ..config import PROJECT_ROOT, AGENTS_ROOT


@dataclass
class CodeEntity:
    """Represents a code entity in the meta lookup system."""
    
    name: str
    type: str  # function, class, agent, template, etc.
    file_path: Path
    line_start: int
    line_end: int
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "file_path": str(self.file_path),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "metadata": self.metadata
        }


class MetaLookupSystem:
    """
    Provides intelligent lookup and understanding of the codebase.
    Knows exactly where everything is and how it relates.
    """
    
    def __init__(self):
        """Initialize the meta lookup system."""
        self.entities: Dict[str, CodeEntity] = {}
        self.type_index: Dict[str, List[str]] = {}
        self.file_index: Dict[str, List[str]] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        
        # Build initial index
        self.rebuild_index()
    
    def rebuild_index(self) -> None:
        """Rebuild the complete code index."""
        self.entities.clear()
        self.type_index.clear()
        self.file_index.clear()
        self.dependency_graph.clear()
        
        # Index main warpengine modules
        src_dir = PROJECT_ROOT / "src" / "warpengine"
        if src_dir.exists():
            self._index_directory(src_dir)
        
        # Index agents
        if AGENTS_ROOT.exists():
            self._index_agents()
        
        # Build dependency graph
        self._build_dependency_graph()
    
    def _index_directory(self, directory: Path) -> None:
        """Index all Python files in a directory."""
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                self._index_file(py_file)
            except Exception:
                # Skip files that can't be parsed
                pass
    
    def _index_file(self, file_path: Path) -> None:
        """Index a single Python file."""
        content = file_path.read_text()
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        # Extract entities
        for node in ast.walk(tree):
            entity = None
            
            if isinstance(node, ast.FunctionDef):
                entity = CodeEntity(
                    name=node.name,
                    type="function",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    metadata={"async": isinstance(node, ast.AsyncFunctionDef)}
                )
            
            elif isinstance(node, ast.ClassDef):
                entity = CodeEntity(
                    name=node.name,
                    type="class",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    metadata={"bases": [self._get_name(base) for base in node.bases]}
                )
            
            if entity:
                entity_id = f"{file_path.stem}.{entity.name}"
                self.entities[entity_id] = entity
                
                # Update indices
                if entity.type not in self.type_index:
                    self.type_index[entity.type] = []
                self.type_index[entity.type].append(entity_id)
                
                file_key = str(file_path)
                if file_key not in self.file_index:
                    self.file_index[file_key] = []
                self.file_index[file_key].append(entity_id)
    
    def _index_agents(self) -> None:
        """Index all agents in the agents directory."""
        for agent_dir in AGENTS_ROOT.iterdir():
            if not agent_dir.is_dir():
                continue
            
            runner_file = agent_dir / "runner.py"
            if runner_file.exists():
                entity = CodeEntity(
                    name=agent_dir.name,
                    type="agent",
                    file_path=runner_file,
                    line_start=1,
                    line_end=len(runner_file.read_text().splitlines()),
                    metadata={"agent_slug": agent_dir.name}
                )
                
                entity_id = f"agent.{agent_dir.name}"
                self.entities[entity_id] = entity
                
                if "agent" not in self.type_index:
                    self.type_index["agent"] = []
                self.type_index["agent"].append(entity_id)
    
    def _build_dependency_graph(self) -> None:
        """Build the dependency graph between entities."""
        for entity_id, entity in self.entities.items():
            if not entity.file_path.exists():
                continue
            
            content = entity.file_path.read_text()
            
            # Find imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            entity.dependencies.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            entity.dependencies.add(node.module)
            except:
                pass
            
            # Update dependency graph
            self.dependency_graph[entity_id] = entity.dependencies
    
    def find_entity(self, name: str, entity_type: Optional[str] = None) -> Optional[CodeEntity]:
        """
        Find an entity by name and optional type.
        
        Args:
            name: Entity name
            entity_type: Optional entity type filter
            
        Returns:
            Found entity or None
        """
        # Try exact match
        if name in self.entities:
            entity = self.entities[name]
            if not entity_type or entity.type == entity_type:
                return entity
        
        # Try partial match
        for entity_id, entity in self.entities.items():
            if entity.name == name:
                if not entity_type or entity.type == entity_type:
                    return entity
        
        return None
    
    def find_entities_by_type(self, entity_type: str) -> List[CodeEntity]:
        """
        Find all entities of a specific type.
        
        Args:
            entity_type: Entity type
            
        Returns:
            List of entities
        """
        entity_ids = self.type_index.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids]
    
    def find_safe_injection_point(
        self,
        file_path: Path,
        entity_type: str
    ) -> Optional[int]:
        """
        Find a safe line number to inject code without breaking existing code.
        
        Args:
            file_path: Target file
            entity_type: Type of entity to inject
            
        Returns:
            Safe line number or None
        """
        file_key = str(file_path)
        existing_entities = self.file_index.get(file_key, [])
        
        if not existing_entities:
            # File has no indexed entities, safe to append
            return -1  # Indicates end of file
        
        # Find the last entity of the same type
        last_line = 0
        for entity_id in existing_entities:
            entity = self.entities[entity_id]
            if entity.type == entity_type:
                last_line = max(last_line, entity.line_end)
        
        if last_line > 0:
            # Insert after the last entity of the same type
            return last_line + 2  # Leave a blank line
        
        # No entities of this type, find appropriate section
        if entity_type in ["function", "class"]:
            # After imports
            content = file_path.read_text()
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    last_line = i
            return last_line + 2 if last_line > 0 else 10
        
        return -1  # Default to end of file
    
    def get_entity_context(self, entity_id: str) -> Dict[str, Any]:
        """
        Get the complete context for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Entity context including dependencies and dependents
        """
        if entity_id not in self.entities:
            return {}
        
        entity = self.entities[entity_id]
        
        # Find dependents
        dependents = set()
        for other_id, deps in self.dependency_graph.items():
            if entity_id in deps or entity.name in deps:
                dependents.add(other_id)
        
        entity.dependents = dependents
        
        return {
            "entity": entity.to_dict(),
            "dependencies": [
                self.entities.get(dep, {"name": dep}).to_dict() if isinstance(self.entities.get(dep), CodeEntity) else {"name": dep}
                for dep in entity.dependencies
            ],
            "dependents": [
                self.entities[dep].to_dict()
                for dep in dependents
                if dep in self.entities
            ],
            "related_entities": self._find_related_entities(entity_id)
        }
    
    def _find_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Find entities related to the given entity."""
        if entity_id not in self.entities:
            return []
        
        entity = self.entities[entity_id]
        related = []
        
        # Find entities in the same file
        file_key = str(entity.file_path)
        for other_id in self.file_index.get(file_key, []):
            if other_id != entity_id:
                related.append(self.entities[other_id].to_dict())
        
        return related
    
    def _get_name(self, node: ast.AST) -> str:
        """Get the name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return "unknown"
