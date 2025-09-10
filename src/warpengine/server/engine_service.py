"""
Warp Engine Service - Server-based Agent Engine with REST API
This runs as a persistent service that Warp Terminal can interact with programmatically.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..agent_builder.enhanced_generator import EnhancedAgentBuilder, AgentType
from ..registry.registry import list_agents, get_agent, upsert_agent, load_registry, delete_agent
from ..orchestrator.chain import run_three_agent_workflow
from ..storage.cache import new_job_id, put_record, get_record
from ..config import PROJECT_ROOT, DATA_DIR


class JobStatus(Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Represents an async job."""

    id: str
    command: str
    status: JobStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: int = 0
    logs: List[str] = None

    def __post_init__(self):
        if self.logs is None:
            self.logs = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        return data


class WarpEngineService:
    """Main service class for Warp Engine."""

    def __init__(self):
        """Initialize the service."""
        self.jobs: Dict[str, Job] = {}
        self.active_websockets: List[WebSocket] = []
        self.builder = EnhancedAgentBuilder()
        self.running = False

        # Ensure data directories exist
        (DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
        (DATA_DIR / "jobs").mkdir(parents=True, exist_ok=True)

    async def start(self):
        """Start the service."""
        self.running = True
        self._log("service", "Warp Engine Service started")

    async def stop(self):
        """Stop the service."""
        self.running = False
        self._log("service", "Warp Engine Service stopped")

    def _log(self, category: str, message: str):
        """Log a message."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{category.upper()}] {message}"
        print(log_entry)

        # Save to log file
        log_file = (
            DATA_DIR / "logs" / f"service_{datetime.now().strftime('%Y%m%d')}.log"
        )
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")

    async def broadcast_update(self, job: Job):
        """Broadcast job update to all connected WebSocket clients."""
        message = json.dumps({"type": "job_update", "job": job.to_dict()})

        for websocket in self.active_websockets:
            try:
                await websocket.send_text(message)
            except:
                self.active_websockets.remove(websocket)

    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> Job:
        """Execute a command asynchronously."""
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id, command=command, status=JobStatus.PENDING, created_at=time.time()
        )

        self.jobs[job_id] = job
        self._log("job", f"Created job {job_id} for command: {command}")

        # Execute in background
        asyncio.create_task(self._execute_job(job, params))

        return job

    async def _execute_job(self, job: Job, params: Dict[str, Any] = None):
        """Execute a job in the background."""
        try:
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            job.logs.append(f"Starting execution of command: {job.command}")
            await self.broadcast_update(job)

            # Route to appropriate handler
            if job.command == "create_agent":
                result = await self._create_agent(job, params)
            elif job.command == "list_agents":
                result = await self._list_agents(job)
            elif job.command == "run_agent":
                result = await self._run_agent(job, params)
            elif job.command == "get_registry":
                result = await self._get_registry(job)
            elif job.command == "delete_agent":
                result = await self._delete_agent(job, params)
            elif job.command == "update_agent":
                result = await self._update_agent(job, params)
            elif job.command == "server_status":
                result = await self._server_status(job)
            else:
                raise ValueError(f"Unknown command: {job.command}")

            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            job.progress = 100
            job.logs.append(f"Command completed successfully")

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
            job.logs.append(f"Command failed: {e}")
            self._log("error", f"Job {job.id} failed: {e}")

        await self.broadcast_update(job)

        # Save job to disk
        self._save_job(job)

    async def _create_agent(self, job: Job, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent."""
        job.logs.append("Creating new agent...")
        job.progress = 25
        await self.broadcast_update(job)

        # Extract parameters
        agent_type_str = params.get("type", "RESEARCH").upper()

        # Map string to AgentType enum with fallback
        agent_type_map = {
            "RESEARCH": AgentType.RESEARCH,
            "CODE_GENERATOR": AgentType.CODE_GENERATOR,
            "DATA_ANALYST": AgentType.DATA_ANALYST,
            "CUSTOM": AgentType.RESEARCH,  # Default to RESEARCH for CUSTOM
        }

        agent_type = agent_type_map.get(agent_type_str, AgentType.RESEARCH)
        name = params.get("name", "Custom Agent")
        description = params.get("description", "")
        prompts = params.get("prompts", {})

        job.logs.append(f"Agent type: {agent_type.value}")
        job.logs.append(f"Agent name: {name}")
        job.progress = 50
        await self.broadcast_update(job)

        # Create the agent
        slug = self.builder.create_agent_from_template(
            agent_type=agent_type, name=name, description=description, prompts=prompts
        )

        job.logs.append(f"Agent created with slug: {slug}")
        job.progress = 75
        await self.broadcast_update(job)

        # Get the created agent details
        agent = get_agent(slug)

        return {
            "success": True,
            "slug": slug,
            "agent": agent,
            "executable": f"./bin/{slug}",
        }

    async def _list_agents(self, job: Job) -> Dict[str, Any]:
        """List all agents."""
        job.logs.append("Fetching agent list...")
        agents = list_agents()
        job.logs.append(f"Found {len(agents)} agents")
        return {"success": True, "count": len(agents), "agents": agents}

    async def _run_agent(self, job: Job, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run an agent."""
        agent_name = params.get("agent")
        input_text = params.get("input", "")

        job.logs.append(f"Running agent: {agent_name}")
        job.progress = 25
        await self.broadcast_update(job)

        agent = get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent not found: {agent_name}")

        job.logs.append("Executing agent workflow...")
        job.progress = 50
        await self.broadcast_update(job)

        # Import and run the agent
        import importlib

        module_path, func_name = agent["entry"].split(":")
        mod = importlib.import_module(module_path)
        run_fn = getattr(mod, func_name)

        job_id, output = run_fn(input_text)

        job.logs.append(f"Agent execution completed")
        job.progress = 75
        await self.broadcast_update(job)

        return {
            "success": True,
            "job_id": job_id,
            "output": output,
            "agent": agent_name,
        }

    async def _get_registry(self, job: Job) -> Dict[str, Any]:
        """Get the agent registry."""
        job.logs.append("Loading agent registry...")
        registry = load_registry()
        job.logs.append(
            f"Registry loaded with {len(registry.get('agents', []))} agents"
        )
        return {"success": True, "registry": registry}

    async def _delete_agent(self, job: Job, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an agent."""
        agent_slug = params.get("agent")
        if not agent_slug:
            raise ValueError("Agent slug required for deletion")

        job.logs.append(f"Deleting agent: {agent_slug}")
        job.progress = 25
        await self.broadcast_update(job)

        # Check if agent exists
        agent = get_agent(agent_slug)
        if not agent:
            raise ValueError(f"Agent not found: {agent_slug}")

        job.logs.append("Agent found, cleaning up files...")
        job.progress = 50
        await self.broadcast_update(job)

        # Delete the agent
        success = delete_agent(agent_slug)

        if success:
            job.logs.append(f"Successfully deleted agent: {agent_slug}")
            return {
                "success": True,
                "message": f"Agent '{agent_slug}' deleted successfully",
                "deleted_agent": agent
            }
        else:
            raise ValueError(f"Failed to delete agent: {agent_slug}")

    async def _update_agent(self, job: Job, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent."""
        agent_slug = params.get("agent")
        if not agent_slug:
            raise ValueError("Agent slug required for update")

        job.logs.append(f"Updating agent: {agent_slug}")
        job.progress = 25
        await self.broadcast_update(job)

        # Check if agent exists
        existing_agent = get_agent(agent_slug)
        if not existing_agent:
            raise ValueError(f"Agent not found: {agent_slug}")

        job.logs.append("Agent found, preparing update...")
        job.progress = 50
        await self.broadcast_update(job)

        # Merge updates with existing agent
        updated_agent = existing_agent.copy()
        updated_agent.update(params.get("updates", {}))
        updated_agent["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Regenerate the agent with updates
        upsert_agent(updated_agent)

        job.logs.append(f"Successfully updated agent: {agent_slug}")
        return {
            "success": True,
            "message": f"Agent '{agent_slug}' updated successfully",
            "updated_agent": updated_agent
        }

    async def _server_status(self, job: Job) -> Dict[str, Any]:
        """Get server status."""
        first_job_time = 0
        if self.jobs:
            first_job_key = list(self.jobs.keys())[0]
            first_job_time = self.jobs[first_job_key].created_at

        # Get API usage stats if available
        usage_stats = {}
        try:
            from ..api.client import A2AClient
            client = A2AClient()
            if hasattr(client, 'openai_client') and client.openai_client:
                usage_stats = client.openai_client.get_usage_stats()
        except:
            pass

        return {
            "success": True,
            "running": self.running,
            "jobs_total": len(self.jobs),
            "jobs_pending": len(
                [j for j in self.jobs.values() if j.status == JobStatus.PENDING]
            ),
            "jobs_running": len(
                [j for j in self.jobs.values() if j.status == JobStatus.RUNNING]
            ),
            "jobs_completed": len(
                [j for j in self.jobs.values() if j.status == JobStatus.COMPLETED]
            ),
            "jobs_failed": len(
                [j for j in self.jobs.values() if j.status == JobStatus.FAILED]
            ),
            "websocket_connections": len(self.active_websockets),
            "uptime": time.time() - first_job_time if first_job_time else 0,
            "api_usage": usage_stats,
        }

    def _save_job(self, job: Job):
        """Save job to disk."""
        job_file = DATA_DIR / "jobs" / f"{job.id}.json"
        with open(job_file, "w") as f:
            json.dump(job.to_dict(), f, indent=2)

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self.jobs.get(job_id)


# Create FastAPI app
app = FastAPI(
    title="Warp Engine Service",
    description="Server-based Agent Engine with REST API",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create service instance
service = WarpEngineService()


@app.on_event("startup")
async def startup_event():
    """Start the service on app startup."""
    await service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the service on app shutdown."""
    await service.stop()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with web interface."""
    agents = list_agents()
    agent_list = "".join([
        f'<li><a href="/ui/agent/{a["slug"]}">{a["name"]}</a> - {a.get("description", "")}</li>'
        for a in agents
    ])

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Warp Engine Service</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f8fafc; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
            .status {{ background: #22c55e; color: white; padding: 5px 10px; border-radius: 20px; display: inline-block; font-size: 14px; }}
            .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            .agents {{ list-style: none; padding: 0; }}
            .agents li {{ padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
            .agents li:last-child {{ border-bottom: none; }}
            .agents a {{ color: #3b82f6; text-decoration: none; font-weight: 500; }}
            .agents a:hover {{ text-decoration: underline; }}
            .endpoint {{ font-family: 'Courier New', monospace; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 14px; }}
            .btn {{ background: #3b82f6; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: 500; }}
            .btn:hover {{ background: #2563eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Warp Engine Service</h1>
                <p>Universal Agent Protocol v2.0.0</p>
                <span class="status">{'RUNNING' if service.running else 'STOPPED'}</span>
            </div>

            <div class="card">
                <h2>🤖 Registered Agents ({len(agents)})</h2>
                <ul class="agents">
                    {agent_list}
                </ul>
                <a href="/api/agents" class="btn" target="_blank">View JSON API</a>
            </div>

            <div class="card">
                <h2>🔌 API Endpoints</h2>
                <p><strong>Commands:</strong> <code class="endpoint">POST /api/command</code></p>
                <p><strong>Jobs:</strong> <code class="endpoint">GET /api/jobs/{{job_id}}</code></p>
                <p><strong>Status:</strong> <code class="endpoint">GET /api/status</code></p>
                <p><strong>WebSocket:</strong> <code class="endpoint">ws://127.0.0.1:8788/ws</code></p>
            </div>

            <div class="card">
                <h2>💻 Service Management</h2>
                <pre>
./warp-engine-service status    # Check service status
./warp-engine-service restart   # Restart service
./warp-engine-service logs      # View logs
./warp-engine-client ai         # Natural language interface
                </pre>
            </div>
        </div>
    </body>
    </html>
    """


@app.post("/api/command")
async def execute_command(command: Dict[str, Any]):
    """Execute a command asynchronously."""
    cmd = command.get("command")
    params = command.get("params", {})

    if not cmd:
        return JSONResponse({"error": "No command specified"}, status_code=400)

    job = await service.execute_command(cmd, params)

    return {
        "job_id": job.id,
        "status": job.status.value,
        "message": f"Command '{cmd}' queued for execution",
    }


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and result."""
    job = service.get_job(job_id)

    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)

    return job.to_dict()


@app.get("/api/jobs/{job_id}/logs")
async def get_job_logs(job_id: str):
    """Stream job logs."""
    job = service.get_job(job_id)

    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)

    async def generate():
        """Generate log stream."""
        last_index = 0
        while job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            if len(job.logs) > last_index:
                for log in job.logs[last_index:]:
                    yield f"data: {json.dumps({'log': log})}\n\n"
                last_index = len(job.logs)
            await asyncio.sleep(0.5)

        # Send final logs
        for log in job.logs[last_index:]:
            yield f"data: {json.dumps({'log': log})}\n\n"

        # Send completion
        yield f"data: {json.dumps({'status': job.status.value, 'result': job.result})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/agents")
async def get_agents():
    """Get all agents synchronously."""
    agents = list_agents()
    return {"count": len(agents), "agents": agents}


@app.get("/api/status")
async def get_status():
    """Get service status."""
    try:
        # Call the status method directly instead of using the job queue
        first_job_time = 0
        if service.jobs:
            first_job_key = list(service.jobs.keys())[0]
            first_job_time = service.jobs[first_job_key].created_at

        status = {
            "success": True,
            "running": service.running,
            "jobs_total": len(service.jobs),
            "jobs_pending": len(
                [j for j in service.jobs.values() if j.status == JobStatus.PENDING]
            ),
            "jobs_running": len(
                [j for j in service.jobs.values() if j.status == JobStatus.RUNNING]
            ),
            "jobs_completed": len(
                [j for j in service.jobs.values() if j.status == JobStatus.COMPLETED]
            ),
            "jobs_failed": len(
                [j for j in service.jobs.values() if j.status == JobStatus.FAILED]
            ),
            "websocket_connections": len(service.active_websockets),
            "uptime": time.time() - first_job_time if first_job_time else 0,
        }

        return status
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/ui/agent/{slug}", response_class=HTMLResponse)
async def ui_agent(slug: str) -> str:
    """Simple Web UI for running an agent with user-provided input (e.g., website vibe)."""
    # Basic validation: ensure agent exists
    agent = get_agent(slug)
    if not agent:
        return HTMLResponse(
            content=f"<html><body><h3>Agent '{slug}' not found.</h3></body></html>",
            status_code=404,
        )

    return f"""
    <html>
      <head>
        <meta charset=\"utf-8\" />
        <title>Warp Engine • Run Agent: {slug}</title>
        <style>
          body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; margin: 24px; }}
          .card {{ max-width: 900px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 8px; }}
          label {{ display: block; margin-bottom: 8px; font-weight: 600; }}
          input[type=text] {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; }}
          button {{ margin-top: 12px; padding: 10px 16px; background: #4f46e5; color: #fff; border: 0; border-radius: 6px; cursor: pointer; }}
          pre {{ background: #0b1020; color: #c9d1d9; padding: 16px; border-radius: 6px; overflow-x: auto; }}
          .muted {{ color: #6b7280; font-size: 12px; }}
          .log {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }}
        </style>
      </head>
      <body>
        <div class=\"card\">
          <h2>Run Agent: {agent.get('name', slug)}</h2>
          <p class=\"muted\">Slug: {slug}</p>
          <label for=\"input\">Input (e.g., website vibe):</label>
          <input type=\"text\" id=\"input\" placeholder=\"e.g., cyberpunk neon portfolio\" />
          <button onclick=\"runAgent()\">Run</button>

          <div id=\"status\" style=\"margin-top:16px;\"></div>
          <h3>Logs</h3>
          <pre id=\"logs\" class=\"log\"></pre>
          <h3>Output</h3>
          <pre id=\"output\"></pre>
        </div>

        <script>
          async function runAgent() {{
            const input = document.getElementById('input').value || '';
            const status = document.getElementById('status');
            const logs = document.getElementById('logs');
            const output = document.getElementById('output');
            status.textContent = 'Submitting job...';
            logs.textContent = '';
            output.textContent = '';

            try {{
              const resp = await fetch('/api/command', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                  command: 'run_agent',
                  params: {{ agent: '{slug}', input }}
                }})
              }});
              const data = await resp.json();
              if (!resp.ok) {{
                status.textContent = 'Error: ' + (data.error || 'Failed to submit job');
                return;
              }}
              const jobId = data.job_id;
              status.textContent = 'Job submitted: ' + jobId;

              // Stream logs via SSE
              const evt = new EventSource(`/api/jobs/${{jobId}}/logs`);
              evt.onmessage = (e) => {{
                try {{
                  const payload = JSON.parse(e.data);
                  if (payload.log) {{
                    logs.textContent += payload.log + '\n';
                  }} else if (payload.status) {{
                    status.textContent = 'Job ' + payload.status;
                    if (payload.result && payload.result.output) {{
                      output.textContent = payload.result.output;
                    }}
                    evt.close();
                  }}
                }} catch {{ /* ignore */ }}
              }};
            }} catch (e) {{
              status.textContent = 'Error: ' + e.toString();
            }}
          }}
        </script>
      </body>
    </html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    service.active_websockets.append(websocket)

    try:
        await websocket.send_text(
            json.dumps(
                {"type": "connected", "message": "Connected to Warp Engine Service"}
            )
        )

        while True:
            # Receive commands via WebSocket
            data = await websocket.receive_text()
            command = json.loads(data)

            if command.get("type") == "execute":
                job = await service.execute_command(
                    command.get("command"), command.get("params", {})
                )

                await websocket.send_text(
                    json.dumps({"type": "job_created", "job_id": job.id})
                )

    except WebSocketDisconnect:
        service.active_websockets.remove(websocket)


def run_service(host: str = "127.0.0.1", port: int = 8788):
    """Run the service."""
    print(f"Starting Warp Engine Service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
