#!/usr/bin/env python3
"""
Warp Engine - Main Entry Point for Deployment
This is the entry point for cloud deployment platforms.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set up environment
os.environ.setdefault("WARP_ENGINE_HOST", "0.0.0.0")
os.environ.setdefault("WARP_ENGINE_PORT", "8787")

def main():
    """Main entry point for deployment."""
    try:
        from warpengine.server.engine_service import run_service
        
        # Get host and port from environment
        host = os.environ.get("WARP_ENGINE_HOST", "0.0.0.0")
        port = int(os.environ.get("WARP_ENGINE_PORT", "8787"))
        
        print(f"🚀 Starting Warp Engine Service on {host}:{port}")
        print(f"📊 API: http://{host}:{port}/")
        print(f"🔌 WebSocket: ws://{host}:{port}/ws")
        print(f"🔧 MCP Transport: stdio")
        
        # Start the service
        run_service(host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
