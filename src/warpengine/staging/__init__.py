"""
Staging System - Meta-tagging and intelligent code evolution
This module provides the staging infrastructure for the Warp Engine protocol.
"""

from .stage_manager import StageManager, Stage, StageTag
from .code_injector import CodeInjector, CodeBlock
from .meta_lookup import MetaLookupSystem

__all__ = [
    'StageManager',
    'Stage', 
    'StageTag',
    'CodeInjector',
    'CodeBlock',
    'MetaLookupSystem'
]
