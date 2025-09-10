# 🚀 Warp Engine Service Architecture

## Overview

The Warp Engine has been transformed into a **persistent service architecture** that runs as a daemon and accepts commands via REST API, WebSocket, and command-line interfaces. This enables Warp Terminal to interact with the engine programmatically without human intervention.

---

## Architecture Components

### 1. **Engine Service** (`warp-engine-service`)
- Runs as a background daemon
- REST API on port 8788
- WebSocket support for real-time updates
- Async job processing with queue
- Persistent job storage

### 2. **Engine Client** (`warp-engine-client`)
- Command-line interface to the service
- Natural language processing interface
- Programmatic Python API
- Real-time status monitoring

### 3. **Warp AI Interface**
- High-level abstraction for AI agents
- Natural language understanding
- Automatic command routing
- Response formatting

---

## Service Endpoints

### REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info and available endpoints |
| `/api/command` | POST | Execute async command |
| `/api/jobs/{job_id}` | GET | Get job status and result |
| `/api/jobs/{job_id}/logs` | GET | Stream job logs (SSE) |
| `/api/agents` | GET | List all agents |
| `/api/status` | GET | Service status and metrics |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws` | Real-time bidirectional communication |

---

## Command Flow

```
1. Warp Terminal sends command
        ↓
2. Service receives via API/WebSocket
        ↓
3. Job created and queued
        ↓
4. Async execution begins
        ↓
5. Progress updates via WebSocket
        ↓
6. Result returned to client
        ↓
7. Warp Terminal processes response
```

---

## Available Commands

### Service Management
```bash
# Start the service
./warp-engine-service start

# Stop the service
./warp-engine-service stop

# Check status
./warp-engine-service status

# View logs
./warp-engine-service logs

# Follow logs in real-time
./warp-engine-service follow
```

### Client Commands
```bash
# Check service status
./warp-engine-client status

# List all agents
./warp-engine-client list

# Create agent interactively
./warp-engine-client create

# Run an agent
./warp-engine-client run <agent_name> "input text"

# Natural language interface
./warp-engine-client ai

# Execute raw command
./warp-engine-client exec <command> --params '{"key": "value"}'
```

---

## Python API Usage

```python
from warpengine.client import WarpEngineClient

# Initialize client
client = WarpEngineClient("http://127.0.0.1:8788")

# Check if service is running
if client.is_running():
    # Create an agent
    result = client.create_agent(
        name="My Agent",
        agent_type="RESEARCH",
        description="Research agent for my topic"
    )
    
    # Run the agent
    output = client.run_agent("my_agent", "Research quantum computing")
    
    # Get service status
    status = client.get_status()
```

---

## Natural Language Interface

The AI interface understands natural language commands:

```python
from warpengine.client import WarpAIInterface

ai = WarpAIInterface()

# Process natural language
response = ai.process_user_request("Create an agent that analyzes code")
response = ai.process_user_request("List all my agents")
response = ai.process_user_request("Run the code analyzer on my project")
```

---

## Async Job Processing

Jobs are processed asynchronously with real-time updates:

```python
# Submit command without waiting
job = client.execute_command("create_agent", params, wait=False)

# Check job status
while job.status == "running":
    status = client.get_job(job.job_id)
    print(f"Progress: {status['progress']}%")
    time.sleep(1)

# Get result
result = status['result']
```

---

## WebSocket Integration

For real-time bidirectional communication:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://127.0.0.1:8788/ws');

// Send command
ws.send(JSON.stringify({
    type: 'execute',
    command: 'create_agent',
    params: { name: 'My Agent' }
}));

// Receive updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'job_update') {
        console.log(`Job ${data.job.id}: ${data.job.status}`);
    }
};
```

---

## Logging and Monitoring

### Log Files
- Service logs: `data/logs/service.log`
- Daily logs: `data/logs/service_YYYYMMDD.log`
- Job records: `data/jobs/{job_id}.json`

### Monitoring Metrics
- Total jobs processed
- Jobs by status (pending/running/completed/failed)
- WebSocket connections
- Service uptime

---

## Integration with Warp Terminal

### Scenario 1: Warp AI Creates Agent
```
1. User: "Create an agent for Python code analysis"
2. Warp AI → POST /api/command
   { "command": "create_agent", "params": {...} }
3. Service creates agent asynchronously
4. Warp AI receives job_id
5. Warp AI polls or connects via WebSocket
6. Agent creation completes
7. Warp AI: "✅ Created Python analyzer agent"
```

### Scenario 2: Continuous Operation
```
1. Warp Terminal starts service on boot
2. Service runs persistently in background
3. Multiple Warp windows can connect
4. Agents shared across all terminals
5. Real-time updates via WebSocket
```

---

## Key Features

### ✅ **Non-Blocking Operations**
- All commands execute asynchronously
- Multiple jobs can run concurrently
- No waiting for user input

### ✅ **Persistent State**
- Jobs saved to disk
- Registry persists across restarts
- Agents available immediately

### ✅ **Real-Time Updates**
- WebSocket for live progress
- Server-Sent Events for log streaming
- Instant status queries

### ✅ **Programmatic Control**
- Full API access
- Python client library
- Natural language processing

### ✅ **Robust Error Handling**
- Job retry mechanisms
- Graceful failure recovery
- Detailed error logging

---

## Example: Complete Workflow

```bash
# 1. Start the service
./warp-engine-service start

# 2. Warp Terminal connects
curl http://127.0.0.1:8788/

# 3. Create agent via API
curl -X POST http://127.0.0.1:8788/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "create_agent", "params": {"name": "Code Reviewer"}}'

# 4. Get job status
curl http://127.0.0.1:8788/api/jobs/{job_id}

# 5. Run the agent
curl -X POST http://127.0.0.1:8788/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "run_agent", "params": {"agent": "code_reviewer", "input": "review my code"}}'

# 6. Stream results
curl http://127.0.0.1:8788/api/jobs/{job_id}/logs
```

---

## Summary

The Warp Engine Service provides:
- **Persistent background operation** - No interactive prompts
- **Full API access** - REST, WebSocket, and CLI
- **Async processing** - Non-blocking operations
- **Real-time updates** - Live progress and logs
- **Natural language** - AI-friendly interface
- **Scalable architecture** - Ready for production

This architecture enables Warp Terminal to act as an autonomous agent builder, creating and managing AI agents without human intervention.
