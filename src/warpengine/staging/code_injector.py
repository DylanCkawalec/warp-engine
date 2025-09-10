"""
Code Injector - Smart code injection with begin/end markers
Mechanically precise code evolution without destroying existing agents.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeBlock:
    """Represents an injectable code block with markers."""
    
    id: str
    content: str
    begin_marker: str
    end_marker: str
    file_path: Path
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    
    def get_markers(self) -> Tuple[str, str]:
        """Get the begin and end markers."""
        return (self.begin_marker, self.end_marker)


class CodeInjector:
    """
    Smart code injection system that understands code boundaries.
    Uses begin/end markers for mechanical precision.
    """
    
    # Standard marker patterns for the protocol
    MARKER_PATTERNS = {
        "agent": {
            "begin": "# === WARP_ENGINE_AGENT_BEGIN: {agent_slug} ===",
            "end": "# === WARP_ENGINE_AGENT_END: {agent_slug} ==="
        },
        "registry": {
            "begin": "# === WARP_ENGINE_REGISTRY_BEGIN: {entry_id} ===",
            "end": "# === WARP_ENGINE_REGISTRY_END: {entry_id} ==="
        },
        "template": {
            "begin": "# === WARP_ENGINE_TEMPLATE_BEGIN: {template_name} ===",
            "end": "# === WARP_ENGINE_TEMPLATE_END: {template_name} ==="
        },
        "config": {
            "begin": "# === WARP_ENGINE_CONFIG_BEGIN: {config_key} ===",
            "end": "# === WARP_ENGINE_CONFIG_END: {config_key} ==="
        },
        "function": {
            "begin": "# === WARP_ENGINE_FUNCTION_BEGIN: {function_name} ===",
            "end": "# === WARP_ENGINE_FUNCTION_END: {function_name} ==="
        }
    }
    
    def __init__(self):
        """Initialize the code injector."""
        self.injected_blocks: Dict[str, CodeBlock] = {}
    
    def create_block(
        self,
        block_id: str,
        content: str,
        block_type: str,
        **marker_vars
    ) -> CodeBlock:
        """
        Create a code block with appropriate markers.
        
        Args:
            block_id: Unique block identifier
            content: Code content
            block_type: Type of block (agent, registry, etc.)
            **marker_vars: Variables for marker formatting
            
        Returns:
            CodeBlock with markers
        """
        if block_type not in self.MARKER_PATTERNS:
            raise ValueError(f"Unknown block type: {block_type}")
        
        pattern = self.MARKER_PATTERNS[block_type]
        begin_marker = pattern["begin"].format(**marker_vars)
        end_marker = pattern["end"].format(**marker_vars)
        
        # Add markers to content
        marked_content = f"{begin_marker}\n{content}\n{end_marker}"
        
        block = CodeBlock(
            id=block_id,
            content=marked_content,
            begin_marker=begin_marker,
            end_marker=end_marker,
            file_path=Path(""),  # Will be set during injection
        )
        
        self.injected_blocks[block_id] = block
        return block
    
    def inject_block(
        self,
        file_path: Path,
        block: CodeBlock,
        position: Optional[str] = None
    ) -> bool:
        """
        Inject a code block into a file.
        
        Args:
            file_path: Target file path
            block: Code block to inject
            position: Where to inject (end, after_imports, etc.)
            
        Returns:
            True if successful
        """
        if not file_path.exists():
            # Create new file with block
            file_path.write_text(block.content)
            block.file_path = file_path
            return True
        
        content = file_path.read_text()
        lines = content.splitlines()
        
        # Check if block already exists
        if block.begin_marker in content:
            return self.update_block(file_path, block)
        
        # Find injection position
        if position == "after_imports":
            insert_line = self._find_after_imports(lines)
        elif position == "before_main":
            insert_line = self._find_before_main(lines)
        else:
            # Default to end of file
            insert_line = len(lines)
        
        # Inject the block
        new_lines = (
            lines[:insert_line] +
            ["", block.begin_marker] +
            block.content.splitlines() +
            [block.end_marker, ""] +
            lines[insert_line:]
        )
        
        file_path.write_text("\n".join(new_lines))
        block.file_path = file_path
        block.line_start = insert_line + 1
        block.line_end = insert_line + len(block.content.splitlines()) + 2
        
        return True
    
    def update_block(self, file_path: Path, block: CodeBlock) -> bool:
        """
        Update an existing code block.
        
        Args:
            file_path: File containing the block
            block: Updated code block
            
        Returns:
            True if successful
        """
        content = file_path.read_text()
        
        # Find existing block
        pattern = re.compile(
            rf"{re.escape(block.begin_marker)}.*?{re.escape(block.end_marker)}",
            re.DOTALL
        )
        
        if not pattern.search(content):
            return False
        
        # Replace block content
        new_content = pattern.sub(
            f"{block.begin_marker}\n{block.content}\n{block.end_marker}",
            content
        )
        
        file_path.write_text(new_content)
        return True
    
    def remove_block(self, file_path: Path, block_id: str) -> bool:
        """
        Remove a code block from a file.
        
        Args:
            file_path: File containing the block
            block_id: Block identifier
            
        Returns:
            True if successful
        """
        if block_id not in self.injected_blocks:
            return False
        
        block = self.injected_blocks[block_id]
        content = file_path.read_text()
        
        # Find and remove block
        pattern = re.compile(
            rf"{re.escape(block.begin_marker)}.*?{re.escape(block.end_marker)}\n?",
            re.DOTALL
        )
        
        if not pattern.search(content):
            return False
        
        new_content = pattern.sub("", content)
        file_path.write_text(new_content)
        
        del self.injected_blocks[block_id]
        return True
    
    def find_blocks(self, file_path: Path) -> List[CodeBlock]:
        """
        Find all marked code blocks in a file.
        
        Args:
            file_path: File to search
            
        Returns:
            List of found code blocks
        """
        if not file_path.exists():
            return []
        
        content = file_path.read_text()
        blocks = []
        
        # Search for all marker patterns
        for block_type, pattern in self.MARKER_PATTERNS.items():
            # Create regex for this block type
            begin_pattern = pattern["begin"].replace("{", r"\{").replace("}", r"\}")
            begin_pattern = begin_pattern.replace(r"\{[^}]+\}", r"[^=]+")
            
            end_pattern = pattern["end"].replace("{", r"\{").replace("}", r"\}")
            end_pattern = end_pattern.replace(r"\{[^}]+\}", r"[^=]+")
            
            regex = re.compile(
                rf"({begin_pattern})\n(.*?)\n({end_pattern})",
                re.DOTALL
            )
            
            for match in regex.finditer(content):
                begin_marker = match.group(1)
                block_content = match.group(2)
                end_marker = match.group(3)
                
                # Extract ID from marker
                id_match = re.search(r": ([^=]+) ===", begin_marker)
                block_id = id_match.group(1).strip() if id_match else f"{block_type}_unknown"
                
                blocks.append(CodeBlock(
                    id=block_id,
                    content=block_content,
                    begin_marker=begin_marker,
                    end_marker=end_marker,
                    file_path=file_path
                ))
        
        return blocks
    
    def _find_after_imports(self, lines: List[str]) -> int:
        """Find the line number after all imports."""
        last_import = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")):
                last_import = i
        
        return last_import + 1 if last_import > 0 else 0
    
    def _find_before_main(self, lines: List[str]) -> int:
        """Find the line number before if __name__ == '__main__'."""
        for i, line in enumerate(lines):
            if "__name__" in line and "__main__" in line:
                return i - 1 if i > 0 else 0
        
        return len(lines)
