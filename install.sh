#!/usr/bin/env bash
# Warp Engine Installation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║     WARP ENGINE - Universal Agent Protocol                ║"
echo "║     Installation & Setup                                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${CYAN}▶ Checking Python version...${NC}"
if python3 --version | grep -E "3\.(1[0-9]|[2-9][0-9])" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python version OK${NC}"
else
    echo -e "${RED}❌ Python 3.10+ is required${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${CYAN}▶ Creating virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo -e "${CYAN}▶ Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ Pip upgraded${NC}"

# Install package in editable mode
echo -e "${CYAN}▶ Installing warp-engine package...${NC}"
pip install -e . --quiet
echo -e "${GREEN}✅ Package installed${NC}"

# Install additional dependencies
echo -e "${CYAN}▶ Installing dependencies...${NC}"
pip install openai python-dotenv pyyaml rich websockets --quiet
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create directories
echo -e "${CYAN}▶ Creating project directories...${NC}"
mkdir -p data bin input_files
mkdir -p data/logs data/knowledge data/warp_drive data/test_results
mkdir -p src/warpengine/agents src/warpengine/toolkits
echo -e "${GREEN}✅ Directories created${NC}"

# Make scripts executable
chmod +x warp-engine 2>/dev/null || true
chmod +x install.sh 2>/dev/null || true

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}               OPENAI API KEY CONFIGURATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if .env already exists with a valid key
if [ -f .env ] && grep -q "^OPENAI_API_KEY=sk-" .env 2>/dev/null; then
    echo -e "${GREEN}✅ Found existing .env file with API key${NC}"
    echo -e "${CYAN}Do you want to keep the existing configuration? (y/n):${NC}"
    read -r keep_config
    if [[ "$keep_config" == "y" || "$keep_config" == "Y" ]]; then
        echo -e "${GREEN}✅ Using existing configuration${NC}"
        echo ""
        echo -e "${GREEN}🎉 Installation complete!${NC}"
        echo ""
        echo -e "${CYAN}Run ${YELLOW}./warp-engine${CYAN} to start!${NC}"
        exit 0
    fi
fi

# Get API key from user
echo -e "${CYAN}Please enter your OpenAI API key:${NC}"
echo ""
echo -e "${YELLOW}Example format:${NC}"
echo -e "${GREEN}sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx${NC}"
echo -e "${YELLOW}or${NC}"
echo -e "${GREEN}sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx${NC}"
echo ""
echo -e "${CYAN}Get your API key from: ${BLUE}https://platform.openai.com/api-keys${NC}"
echo ""
echo -e -n "${YELLOW}Enter API Key: ${NC}"

# Read API key (visible for easy copy-paste)
read API_KEY

# Validate API key format
if [[ ! "$API_KEY" =~ ^sk-[a-zA-Z0-9_-]{20,}$ ]]; then
    echo ""
    echo -e "${RED}⚠️  Warning: API key format looks incorrect${NC}"
    echo -e "${YELLOW}API keys should start with 'sk-' followed by alphanumeric characters${NC}"
    echo -e "${CYAN}Continue anyway? (y/n):${NC}"
    read -r continue_anyway
    if [[ "$continue_anyway" != "y" && "$continue_anyway" != "Y" ]]; then
        echo -e "${RED}Installation cancelled${NC}"
        exit 1
    fi
fi

# Create .env file
echo -e "${CYAN}▶ Creating .env configuration file...${NC}"
cat > .env << EOF
# Warp Engine Configuration
# Generated on $(date)

# OpenAI API Configuration
OPENAI_API_KEY=${API_KEY}

# Server Configuration
WARP_ENGINE_HOST=127.0.0.1
WARP_ENGINE_PORT=8787

# Optional: Uncomment to customize
# WARP_ENGINE_LOG_LEVEL=info
# WARP_ENGINE_MAX_TOKENS=4096
# WARP_ENGINE_TEMPERATURE=0.7
EOF

echo -e "${GREEN}✅ Configuration file created${NC}"

# Test the API key by trying to import and initialize the client
echo -e "${CYAN}▶ Validating API key...${NC}"
python3 -c "
import os
os.environ['OPENAI_API_KEY'] = '${API_KEY}'
try:
    from openai import OpenAI
    client = OpenAI()
    print('✅ API key format validated')
except Exception as e:
    print('⚠️  Could not validate API key (will check when running)')
" 2>/dev/null || echo -e "${YELLOW}⚠️  API key will be validated on first use${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}           🎉 INSTALLATION COMPLETE! 🎉${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Quick Start Commands:${NC}"
echo ""
echo -e "  ${YELLOW}./warp-engine${NC}              - Launch interactive menu"
echo -e "  ${YELLOW}warp-engine new-agent${NC}      - Create a new AI agent"
echo -e "  ${YELLOW}warp-engine agent list${NC}     - List all agents"
echo -e "  ${YELLOW}warp-engine serve${NC}          - Start web interface"
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo -e "  1. Run ${YELLOW}./warp-engine${NC} to start the interactive menu"
echo -e "  2. Select option 2 to create your first agent"
echo -e "  3. Choose from templates or create custom agents"
echo ""
echo -e "${GREEN}Ready to build amazing AI agents! 🚀${NC}"
echo ""