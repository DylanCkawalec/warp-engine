#!/usr/bin/env bash
# Reset/Uninstall Script for Warp Engine

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  Warp Engine Reset/Cleanup Script${NC}"
echo ""
echo "This will remove:"
echo "  - Virtual environment (.venv)"
echo "  - Configuration file (.env)"
echo "  - Generated agents (src/warpengine/agents/*)"
echo "  - Agent binaries (bin/*)"
echo "  - Data files (data/*)"
echo ""
echo -e "${RED}This action cannot be undone!${NC}"
echo ""
read -p "Are you sure you want to reset? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${GREEN}Reset cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Cleaning up...${NC}"

# Remove virtual environment
if [ -d ".venv" ]; then
    echo "  - Removing virtual environment..."
    rm -rf .venv
fi

# Backup .env if it exists
if [ -f ".env" ]; then
    echo "  - Backing up .env to .env.backup..."
    cp .env .env.backup
    rm .env
fi

# Clean generated agents
if [ -d "src/warpengine/agents" ]; then
    echo "  - Cleaning generated agents..."
    find src/warpengine/agents -type f -name "*.py" -not -name "__init__.py" -delete
    find src/warpengine/agents -type d -empty -delete
fi

# Clean binaries
if [ -d "bin" ]; then
    echo "  - Cleaning agent binaries..."
    rm -f bin/*
fi

# Clean data but keep structure
if [ -d "data" ]; then
    echo "  - Cleaning data files..."
    rm -f data/*.json
    rm -f data/logs/*
    rm -f data/knowledge/*
    rm -f data/warp_drive/*
    rm -f data/test_results/*
fi

# Remove Python cache
echo "  - Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove egg-info
if [ -d "src/warp_engine.egg-info" ]; then
    echo "  - Removing egg-info..."
    rm -rf src/warp_engine.egg-info
fi

echo ""
echo -e "${GREEN}✅ Reset complete!${NC}"
echo ""
echo "To set up again, run:"
echo -e "  ${YELLOW}./install.sh${NC}"
echo ""
if [ -f ".env.backup" ]; then
    echo -e "${CYAN}Your API key was backed up to .env.backup${NC}"
fi
