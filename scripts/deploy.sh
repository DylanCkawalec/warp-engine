#!/usr/bin/env bash
# Deployment script for Warp Engine

set -e

echo "🚀 Deploying Warp Engine..."

# Check prerequisites
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run ./install.sh first."
    exit 1
fi

if ! grep -q "^OPENAI_API_KEY=" .env; then
    echo "❌ OPENAI_API_KEY not found in .env"
    exit 1
fi

# Stop existing service
echo "  - Stopping existing service..."
./warp-engine-service stop 2>/dev/null || true

# Run health check
echo "  - Running health checks..."
if ! python3 scripts/health_check.py; then
    echo "❌ Health check failed. Fix issues before deploying."
    exit 1
fi

# Start service
echo "  - Starting service..."
./warp-engine-service start

# Verify deployment
echo "  - Verifying deployment..."
sleep 3

if curl -s "http://127.0.0.1:8788/api/status" | grep -q "success.*true"; then
    echo "✅ Deployment successful!"
    echo ""
    echo "Service is running at:"
    echo "  API: http://127.0.0.1:8788"
    echo "  WebSocket: ws://127.0.0.1:8788/ws"
    echo ""
    echo "Available agents:"
    ./warp-engine-client list
else
    echo "❌ Deployment failed - service not responding"
    exit 1
fi
