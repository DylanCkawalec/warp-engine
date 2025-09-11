#!/usr/bin/env python3
"""
MCP Server for Warp Engine
Simple MCP integration for deployment platforms.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data/mcp_server.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for MCP server."""
    logger.info("🚀 Starting Warp Engine MCP Server")
    
    # Simple MCP transport detection
    transport_type = "stdio"
    logger.info(f"MCP transport: {transport_type}")
    
    try:
        # Start the service
        from warpengine.server.engine_service import run_service
        logger.info("Starting engine service on host=0.0.0.0, port=8787")
        run_service(host="0.0.0.0", port=8787)
    except Exception as e:
        logger.error(f"Failed to start engine service: {e}")
        raise

if __name__ == "__main__":
    main()
