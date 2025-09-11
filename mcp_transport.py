#!/usr/bin/env python3
"""
MCP Transport for Warp Engine
Provides the transport layer that deployment platforms expect.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def run_stdio_transport():
    """Run MCP with stdio transport."""
    print("Starting MCP stdio transport...")
    
    # Start the Warp Engine service
    from warpengine.server.engine_service import run_service
    run_service(host="0.0.0.0", port=8787)

def run_sse_transport():
    """Run MCP with SSE transport."""
    print("Starting MCP SSE transport...")
    
    # Start the Warp Engine service
    from warpengine.server.engine_service import run_service
    run_service(host="0.0.0.0", port=8787)

def run_http_transport():
    """Run MCP with HTTP transport."""
    print("Starting MCP HTTP transport...")
    
    # Start the Warp Engine service
    from warpengine.server.engine_service import run_service
    run_service(host="0.0.0.0", port=8787)

if __name__ == "__main__":
    # Default to stdio transport
    run_stdio_transport()
