# 🚀 **Warp Engine Quick Reference**

## 📋 **Essential Commands**

### Service Management
```bash
# Start Warp Engine service
./warp-engine-service start

# Check status
./warp-engine-service status

# View logs
./warp-engine-service logs

# Restart service
./warp-engine-service restart

# Stop service
./warp-engine-service stop
```

### Client Commands
```bash
# Natural language interface
./warp-engine-client ai

# List all agents
./warp-engine-client list

# Create agent interactively
./warp-engine-client create

# Run specific agent
./warp-engine-client run <agent_slug> "input text"

# Execute raw command
./warp-engine-client exec <command> --params '{"key": "value"}'
```

### Web Interfaces
```bash
# Main dashboard
open http://127.0.0.1:8788

# Agent UI
open http://127.0.0.1:8788/ui/agent/<agent_slug>
```

## 🤖 **Creating Agents with Warp**

### Basic Syntax
```
/warp-engine make me an agent that [description]
```

### Examples
```
/warp-engine make me an agent that analyzes stock data
/warp-engine make me an agent that generates code
/warp-engine make me an agent that researches any topic
/warp-engine make me an agent that creates websites
/warp-engine make me an agent that fetches chicken pictures
```

## 📊 **API Endpoints**

### REST API
```bash
# Execute command
POST http://127.0.0.1:8788/api/command
{
  "command": "create_agent",
  "params": {
    "name": "My Agent",
    "type": "RESEARCH",
    "description": "Agent description"
  }
}

# Get job status
GET http://127.0.0.1:8788/api/jobs/{job_id}

# List agents
GET http://127.0.0.1:8788/api/agents

# Service status
GET http://127.0.0.1:8788/api/status
```

### WebSocket
```javascript
const ws = new WebSocket('ws://127.0.0.1:8788/ws');
ws.send(JSON.stringify({
  type: 'execute',
  command: 'create_agent',
  params: { name: 'Agent Name' }
}));
```

## 🛠️ **Agent Templates**

### Available Types
- **RESEARCH**: Academic research, data analysis
- **CODE_GENERATOR**: Code generation, automation
- **DATA_ANALYST**: Data processing, insights
- **CUSTOM**: Specialized tasks

### Template Features
```python
prompts = {
    "plan": "Strategic planning phase",
    "execute": "Implementation phase",
    "refine": "Optimization and polish phase"
}
```

## 📁 **Project Structure**

```
warp-engine/
├── bin/                    # Executable agents
├── data/
│   ├── logs/              # Service logs
│   ├── jobs/              # Job persistence
│   └── registry.json      # Agent registry
├── src/warpengine/
│   ├── agents/            # Generated agents
│   ├── client/            # API client
│   └── server/            # Service backend
└── scripts/               # Deployment scripts
```

## 🔧 **Maintenance**

### Daily Operations
```bash
# Check health
./warp-engine-service status

# Monitor logs
./warp-engine-service logs

# Backup data
cp -r data data_backup_$(date +%Y%m%d)
```

### Troubleshooting
```bash
# Restart if issues
./warp-engine-service restart

# Clear logs if too large
echo "" > data/logs/service.log

# Check disk space
df -h
```

## 🎯 **Best Practices**

### Agent Creation
1. **Be Specific**: Clear, detailed descriptions
2. **Choose Right Template**: Match task to agent type
3. **Test Thoroughly**: Verify agent works as expected
4. **Document**: Keep track of agent purposes

### Performance
1. **Monitor Resources**: Check memory and CPU usage
2. **Log Rotation**: Regular log cleanup
3. **Backup Regularly**: Important agents and data
4. **Update Dependencies**: Keep packages current

## 🚀 **Quick Agent Examples**

### Research Agent
```
/warp-engine make me an agent that researches quantum computing
```

### Code Generator
```
/warp-engine make me an agent that generates React components
```

### Data Analyst
```
/warp-engine make me an agent that analyzes sales data
```

### Custom Agent
```
/warp-engine make me an agent that fetches and displays chicken pictures
```

## 📞 **Support**

### Common Issues
- **Service won't start**: Check port 8788 availability
- **API key issues**: Verify .env file format
- **Agent creation fails**: Check service logs
- **Web UI not loading**: Verify service is running

### Logs and Debugging
```bash
# Service logs
./warp-engine-service logs

# Job details
curl http://127.0.0.1:8788/api/jobs/{job_id}

# Agent registry
./warp-engine-client exec get_registry
```

---

**Happy agent building!** 🤖✨
