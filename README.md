# 🚀 Warp Engine - Universal Agent Protocol

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/warp-engine)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Warp Engine** is a production-ready, server-based AI agent factory that runs as a persistent service. Create specialized AI agents through natural language commands, with zero manual coding required.

## 🎯 Core Features

- **🔄 Server-Based Architecture**: Persistent daemon with REST API
- **🤖 Agent Factory**: Create specialized agents via natural language
- **⚡ Real-Time Processing**: WebSocket updates and async job queues
- **🛠️ Production Ready**: Docker, health checks, and monitoring
- **🔌 API Integration**: REST, WebSocket, and Python client libraries
- **📊 Monitoring**: Comprehensive logging and metrics

## ✨ Features

### 🤖 **Universal Agent Registry**
- Single source of truth for all agents
- REST API and CLI access
- Version control and lifecycle management
- Agent templates for common use cases

### 🏗️ **Agent Builder Protocol**
- Interactive agent creation via `/new-agent` command
- Pre-built templates: Research, Code Generation, Data Analysis
- Three-agent workflow pattern: Plan → Execute → Refine
- Automatic code generation, testing, and deployment

### 🔌 **Warp Terminal Integration**
- Native integration with Warp's AI features
- Model Context Protocol (MCP) support
- Agent profiles and permissions
- Warp Drive knowledge persistence
- Multi-agent orchestration

### 🎯 **Key Capabilities**
- **Zero-code agent creation** - Build agents through prompts
- **Production-ready output** - Generated agents include tests and documentation
- **Extensible toolkit system** - Add custom agent types and capabilities
- **OpenAI integration** - Powered by GPT-4 and other models
- **Local execution** - All processing happens on your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Warp Terminal](https://www.warp.dev/) (optional but recommended)
- OpenAI API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/warp-engine.git
cd warp-engine
```

2. **Run the launcher:**
```bash
./warp-engine
```

The launcher will:
- Create a virtual environment
- Install dependencies
- Set up configuration
- Launch the interactive menu

3. **Configure your API key:**
```bash
cp env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## 📖 Usage

### Interactive Mode (Recommended)

Run the launcher for an interactive experience:

```bash
./warp-engine
```

This provides a menu-driven interface with options to:
- Create new agents
- List and run existing agents
- Start the web server
- Access the agent registry

### Command Line Interface

#### Create a New Agent

**Interactive mode with templates:**
```bash
warp-engine new-agent --enhanced
```

This will present you with agent templates:
1. 🔬 **Research Agent** - Deep research with multi-page output
2. 💻 **Code Generator** - Production-ready code with tests
3. 📊 **Data Analyst** - Data analysis and insights
4. 🎨 **Custom Agent** - Build from scratch

**Non-interactive mode:**
```bash
warp-engine new-agent \
  --name "Linux Research" \
  --description "Expert Linux system analysis" \
  --plan-prompt "Create a research plan..." \
  --exec-prompt "Execute the research..." \
  --refine-prompt "Polish the output..."
```

#### Run an Agent

```bash
# List available agents
warp-engine agent list

# Run a specific agent
warp-engine agent run --name research_agent

# Or use the generated binary
./bin/research_agent
```

#### Start the Web Server

```bash
warp-engine serve --port 8787 --open-browser
```

Access the UI at `http://localhost:8787`

### API Access

#### Get Agent Registry
```bash
curl http://localhost:8787/api/agents
```

#### Create Agent via API
```bash
curl -X POST http://localhost:8787/api/agents \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "API Agent",
    "description": "Agent created via API",
    "prompts": {
      "plan": "Plan the task",
      "execute": "Execute the plan",
      "refine": "Refine the output"
    }
  }'
```

## 🏗️ Architecture

### Directory Structure
```
warp-engine/
├── config.api.json          # Universal configuration
├── data/
│   ├── registry.json        # Agent registry
│   ├── knowledge/           # Warp Drive cache
│   └── logs/                # Execution logs
├── src/warpengine/
│   ├── agents/              # Generated agents
│   ├── toolkits/            # Agent toolkits
│   ├── warp_integration/    # Warp terminal integration
│   ├── api/                 # API clients (OpenAI, etc.)
│   ├── orchestrator/        # Agent workflow engine
│   └── registry/            # Registry management
├── bin/                     # Executable agent shims
└── tests/                   # Test suite
```

### Agent Lifecycle

```
Create → Build → Test → Deploy → Monitor → Terminate
```

1. **Create**: Define agent via templates or custom prompts
2. **Build**: Generate code and dependencies
3. **Test**: Run automated tests
4. **Deploy**: Create executable and register
5. **Monitor**: Track usage and performance
6. **Terminate**: Clean shutdown and resource cleanup

## 🛠️ Configuration

### Environment Variables

Create a `.env` file with:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional
WARP_ENGINE_HOST=127.0.0.1
WARP_ENGINE_PORT=8787
WARP_ENGINE_MODEL_PLAN=gpt-4-turbo-preview
WARP_ENGINE_MODEL_EXECUTE=gpt-4-turbo-preview
WARP_ENGINE_MODEL_REFINE=gpt-4-turbo-preview
```

### config.api.json

The main configuration file supports:
- Agent templates
- Toolkit definitions
- Model preferences
- Warp integration settings
- Lifecycle configuration

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Test a specific agent:

```bash
pytest src/warpengine/agents/research_agent/test_research_agent.py
```

## 🔧 Advanced Features

### Custom Agent Toolkits

Create specialized toolkits by extending base templates:

```python
# src/warpengine/toolkits/security_audit.py
from warpengine.agent_builder import AgentTemplate, AgentType

class SecurityAuditToolkit(AgentTemplate):
    name = "Security Audit Agent"
    type = AgentType.CUSTOM
    capabilities = ["vulnerability_scanning", "code_analysis", "report_generation"]
    # ... additional configuration
```

### Warp Terminal Integration

When Warp is installed, the engine automatically:
- Creates agent profiles
- Generates workflows
- Enables voice commands
- Syncs with Warp Drive

### Multi-Agent Orchestration

Agents can spawn and coordinate with sub-agents:

```python
# In your agent code
sub_agent_result = run_agent("research_agent", context={"topic": "Linux kernel"})
```

## 📚 Examples

### Research Agent Example

```bash
$ warp-engine new-agent --enhanced
# Select: Research Agent
# Name: Linux Expert

$ echo "Analyze Linux kernel memory management" | ./bin/linux_expert

# Output: Multi-page report with:
# - Executive Summary
# - Technical Analysis
# - Performance Metrics
# - Recommendations
# - References
```

### Code Generator Example

```bash
$ warp-engine agent run --name code_generator
# Input: "Create a REST API for user management with authentication"

# Output: Complete API with:
# - FastAPI application
# - User models
# - Authentication middleware
# - Unit tests
# - OpenAPI documentation
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Warp Terminal](https://www.warp.dev/)
- [OpenAI API](https://platform.openai.com/)
- [Documentation](https://github.com/yourusername/warp-engine/wiki)
- [Issues](https://github.com/yourusername/warp-engine/issues)

## 🙏 Acknowledgments

Built with ❤️ using:
- [Warp Terminal](https://www.warp.dev/) for terminal integration
- [OpenAI](https://openai.com/) for AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output

---

**Note**: Remember to keep your API keys secure and never commit them to version control!