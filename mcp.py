#!/usr/bin/env python3
"""
MCP Integration for Warp Engine
This file provides MCP transport detection for deployment platforms.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# MCP transport detection
def detect_transport():
    """Detect MCP transport type."""
    return "stdio"

def run_mcp():
    """Run MCP server."""
    print("Starting MCP server with stdio transport...")
    
    # Import and run the main service
    from warpengine.server.engine_service import run_service
    run_service(host="0.0.0.0", port=8787)

if __name__ == "__main__":
    # This will be detected by the build system
    transport = detect_transport()
    print(f"MCP transport: {transport}")
    run_mcp()
