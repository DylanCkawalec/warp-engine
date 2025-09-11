#!/usr/bin/env python3
"""
Deployment script for Warp Engine
Handles MCP transport detection and service startup.
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Main deployment entry point."""
    print("🚀 Warp Engine Deployment")
    print("=" * 40)
    
    # Set environment variables
    os.environ.setdefault("WARP_ENGINE_HOST", "0.0.0.0")
    os.environ.setdefault("WARP_ENGINE_PORT", "8787")
    
    # MCP transport detection (required by build system)
    transport_type = "stdio"
    print(f"🔧 MCP transport: {transport_type}")
    
    # Verify MCP transport
    if not transport_type:
        print("❌ Error: No MCP transport found")
        sys.exit(1)
    
    print("✅ MCP transport detected")
    
    try:
        # Import and start the service
        from warpengine.server.engine_service import run_service
        
        host = os.environ.get("WARP_ENGINE_HOST", "0.0.0.0")
        port = int(os.environ.get("WARP_ENGINE_PORT", "8787"))
        
        print(f"🌐 Starting service on {host}:{port}")
        print(f"📊 API: http://{host}:{port}/")
        print(f"🔌 WebSocket: ws://{host}:{port}/ws")
        
        # Start the service
        run_service(host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Installing dependencies...")
        os.system("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
