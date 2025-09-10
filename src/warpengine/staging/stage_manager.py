"""
Stage Manager - Tracks and manages agent creation stages
Each stage is meta-tagged for intelligent understanding and evolution.
"""

from __future__ import annotations
import json
import time
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from ..config import DATA_DIR


class StageTag(Enum):
    """Meta-tags for staging system understanding."""
    
    # Creation stages
    PROMPT_RECEIVED = "prompt_received"
    PROMPT_REFINED = "prompt_refined"
    TEMPLATE_SELECTED = "template_selected"
    CODE_GENERATED = "code_generated"
    CODE_INJECTED = "code_injected"
    TESTS_CREATED = "tests_created"
    AGENT_REGISTERED = "agent_registered"
    BINARY_COMPILED = "binary_compiled"
    
    # Modification stages
    AGENT_UPDATED = "agent_updated"
    AGENT_ENHANCED = "agent_enhanced"
    AGENT_OPTIMIZED = "agent_optimized"
    
    # System stages
    REGISTRY_UPDATED = "registry_updated"
    META_INDEXED = "meta_indexed"
    CONTEXT_CAPTURED = "context_captured"


@dataclass
class Stage:
    """Represents a single stage in the agent creation/modification process."""
    
    id: str
    tag: StageTag
    timestamp: float
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_stage: Optional[str] = None
    child_stages: List[str] = field(default_factory=list)
    
    # Meta-understanding fields
    code_blocks: List[Dict[str, Any]] = field(default_factory=list)
    prompts: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage to dictionary for serialization."""
        return {
            "id": self.id,
            "tag": self.tag.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "metadata": self.metadata,
            "parent_stage": self.parent_stage,
            "child_stages": self.child_stages,
            "code_blocks": self.code_blocks,
            "prompts": self.prompts,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Stage:
        """Create stage from dictionary."""
        return cls(
            id=data["id"],
            tag=StageTag(data["tag"]),
            timestamp=data["timestamp"],
            data=data["data"],
            metadata=data.get("metadata", {}),
            parent_stage=data.get("parent_stage"),
            child_stages=data.get("child_stages", []),
            code_blocks=data.get("code_blocks", []),
            prompts=data.get("prompts", {}),
            context=data.get("context", {})
        )


class StageManager:
    """
    Manages the staging system for agent creation and modification.
    Provides meta-understanding of the entire agent lifecycle.
    """
    
    def __init__(self):
        """Initialize the stage manager."""
        self.stages: Dict[str, Stage] = {}
        self.active_chains: Dict[str, List[str]] = {}
        self.stage_file = DATA_DIR / "stages.json"
        self._load_stages()
    
    def create_stage(
        self,
        tag: StageTag,
        data: Dict[str, Any],
        parent_stage: Optional[str] = None,
        **metadata
    ) -> Stage:
        """
        Create a new stage with meta-tagging.
        
        Args:
            tag: Stage tag for meta-understanding
            data: Stage data
            parent_stage: Parent stage ID if part of a chain
            **metadata: Additional metadata
            
        Returns:
            Created stage
        """
        import uuid
        
        stage_id = str(uuid.uuid4())
        stage = Stage(
            id=stage_id,
            tag=tag,
            timestamp=time.time(),
            data=data,
            metadata=metadata,
            parent_stage=parent_stage
        )
        
        # Link to parent if exists
        if parent_stage and parent_stage in self.stages:
            self.stages[parent_stage].child_stages.append(stage_id)
        
        self.stages[stage_id] = stage
        self._save_stages()
        
        return stage
    
    def add_code_block(self, stage_id: str, code_block: Dict[str, Any]) -> None:
        """
        Add a code block to a stage for meta-understanding.
        
        Args:
            stage_id: Stage ID
            code_block: Code block with markers and content
        """
        if stage_id in self.stages:
            self.stages[stage_id].code_blocks.append(code_block)
            self._save_stages()
    
    def add_prompt(self, stage_id: str, prompt_type: str, prompt: str) -> None:
        """
        Add a prompt to a stage.
        
        Args:
            stage_id: Stage ID
            prompt_type: Type of prompt (original, refined, etc.)
            prompt: Prompt content
        """
        if stage_id in self.stages:
            self.stages[stage_id].prompts[prompt_type] = prompt
            self._save_stages()
    
    def get_stage_chain(self, stage_id: str) -> List[Stage]:
        """
        Get the complete chain of stages from root to current.
        
        Args:
            stage_id: Stage ID
            
        Returns:
            List of stages in chronological order
        """
        chain = []
        current = self.stages.get(stage_id)
        
        # Walk up to root
        while current:
            chain.insert(0, current)
            if current.parent_stage:
                current = self.stages.get(current.parent_stage)
            else:
                break
        
        return chain
    
    def get_latest_stage(self, tag: Optional[StageTag] = None) -> Optional[Stage]:
        """
        Get the most recent stage, optionally filtered by tag.
        
        Args:
            tag: Optional tag filter
            
        Returns:
            Latest stage or None
        """
        stages = list(self.stages.values())
        
        if tag:
            stages = [s for s in stages if s.tag == tag]
        
        if not stages:
            return None
        
        return max(stages, key=lambda s: s.timestamp)
    
    def get_agent_stages(self, agent_slug: str) -> List[Stage]:
        """
        Get all stages related to a specific agent.
        
        Args:
            agent_slug: Agent slug
            
        Returns:
            List of related stages
        """
        agent_stages = []
        
        for stage in self.stages.values():
            if stage.data.get("agent_slug") == agent_slug:
                agent_stages.append(stage)
            elif stage.metadata.get("agent_slug") == agent_slug:
                agent_stages.append(stage)
        
        return sorted(agent_stages, key=lambda s: s.timestamp)
    
    def create_stage_summary(self, stage_id: str) -> Dict[str, Any]:
        """
        Create a comprehensive summary of a stage and its chain.
        
        Args:
            stage_id: Stage ID
            
        Returns:
            Stage summary with full context
        """
        stage = self.stages.get(stage_id)
        if not stage:
            return {}
        
        chain = self.get_stage_chain(stage_id)
        
        summary = {
            "current_stage": stage.to_dict(),
            "chain_length": len(chain),
            "chain_tags": [s.tag.value for s in chain],
            "total_code_blocks": sum(len(s.code_blocks) for s in chain),
            "prompts_evolution": {},
            "context_accumulation": {}
        }
        
        # Track prompt evolution
        for s in chain:
            for prompt_type, prompt in s.prompts.items():
                if prompt_type not in summary["prompts_evolution"]:
                    summary["prompts_evolution"][prompt_type] = []
                summary["prompts_evolution"][prompt_type].append({
                    "stage": s.tag.value,
                    "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt
                })
        
        # Accumulate context
        for s in chain:
            summary["context_accumulation"].update(s.context)
        
        return summary
    
    def _load_stages(self) -> None:
        """Load stages from disk."""
        if self.stage_file.exists():
            try:
                data = json.loads(self.stage_file.read_text())
                self.stages = {
                    sid: Stage.from_dict(sdata)
                    for sid, sdata in data.get("stages", {}).items()
                }
                self.active_chains = data.get("active_chains", {})
            except Exception:
                self.stages = {}
                self.active_chains = {}
    
    def _save_stages(self) -> None:
        """Save stages to disk."""
        self.stage_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "stages": {
                sid: stage.to_dict()
                for sid, stage in self.stages.items()
            },
            "active_chains": self.active_chains
        }
        
        self.stage_file.write_text(json.dumps(data, indent=2))
