"""
Warp Engine Client - Programmatic interface for the Engine Service
This is what Warp Terminal AI would use to interact with the engine.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional, AsyncGenerator
from dataclasses import dataclass

import requests
import websockets
from websockets.exceptions import WebSocketException


@dataclass
class CommandResult:
    """Result of a command execution."""

    job_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: list[str] = None
    duration: float = 0.0


class WarpEngineClient:
    """Client for interacting with Warp Engine Service."""

    def __init__(self, base_url: str = "http://127.0.0.1:8788", timeout: int = 60):
        """Initialize the client.

        Args:
            base_url: Base URL of the engine service
            timeout: Timeout for operations in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.ws_url = base_url.replace("http", "ws") + "/ws"
        self.timeout = timeout
        self.session = requests.Session()

    def is_running(self) -> bool:
        """Check if the service is running."""
        try:
            resp = self.session.get(f"{self.base_url}/", timeout=2)
            return resp.status_code == 200
        except:
            return False

    def execute_command(
        self, command: str, params: Dict[str, Any] = None, wait: bool = True
    ) -> CommandResult:
        """Execute a command.

        Args:
            command: Command to execute
            params: Command parameters
            wait: Whether to wait for completion

        Returns:
            CommandResult with execution details
        """
        start_time = time.time()

        # Submit command
        resp = self.session.post(
            f"{self.base_url}/api/command",
            json={"command": command, "params": params or {}},
            timeout=10,
        )
        resp.raise_for_status()

        data = resp.json()
        job_id = data["job_id"]

        if not wait:
            return CommandResult(job_id=job_id, success=True, logs=[data["message"]])

        # Wait for completion
        result = self._wait_for_job(job_id)
        result.duration = time.time() - start_time

        return result

    def _wait_for_job(self, job_id: str) -> CommandResult:
        """Wait for a job to complete.

        Args:
            job_id: Job ID to wait for

        Returns:
            CommandResult with final status
        """
        start_time = time.time()
        logs = []

        while time.time() - start_time < self.timeout:
            # Get job status
            resp = self.session.get(f"{self.base_url}/api/jobs/{job_id}")

            if resp.status_code == 404:
                return CommandResult(
                    job_id=job_id, success=False, error="Job not found"
                )

            job = resp.json()
            logs = job.get("logs", [])

            if job["status"] == "completed":
                return CommandResult(
                    job_id=job_id, success=True, result=job.get("result"), logs=logs
                )
            elif job["status"] == "failed":
                return CommandResult(
                    job_id=job_id, success=False, error=job.get("error"), logs=logs
                )

            time.sleep(0.5)

        return CommandResult(
            job_id=job_id,
            success=False,
            error="Timeout waiting for job completion",
            logs=logs,
        )

    def create_agent(
        self,
        name: str,
        agent_type: str = "CUSTOM",
        description: str = "",
        prompts: Dict[str, str] = None,
    ) -> CommandResult:
        """Create a new agent.

        Args:
            name: Agent name
            agent_type: Type of agent (RESEARCH, CODE_GENERATOR, DATA_ANALYST, CUSTOM)
            description: Agent description
            prompts: Agent prompts (plan, execute, refine)

        Returns:
            CommandResult with agent details
        """
        params = {
            "name": name,
            "type": agent_type,
            "description": description,
            "prompts": prompts
            or {
                "plan": "Create a comprehensive plan",
                "execute": "Execute the plan thoroughly",
                "refine": "Polish and perfect the output",
            },
        }

        return self.execute_command("create_agent", params)

    def list_agents(self) -> list[Dict[str, Any]]:
        """List all agents.

        Returns:
            List of agent details
        """
        resp = self.session.get(f"{self.base_url}/api/agents")
        resp.raise_for_status()
        return resp.json()["agents"]

    def run_agent(self, agent_name: str, input_text: str) -> CommandResult:
        """Run an agent.

        Args:
            agent_name: Name/slug of the agent
            input_text: Input for the agent

        Returns:
            CommandResult with agent output
        """
        params = {"agent": agent_name, "input": input_text}

        return self.execute_command("run_agent", params)

    def get_status(self) -> Dict[str, Any]:
        """Get service status.

        Returns:
            Service status details
        """
        resp = self.session.get(f"{self.base_url}/api/status")
        resp.raise_for_status()
        return resp.json()

    async def stream_logs(self, job_id: str) -> AsyncGenerator[str, None]:
        """Stream logs for a job.

        Args:
            job_id: Job ID to stream logs for

        Yields:
            Log messages
        """
        url = f"{self.base_url}/api/jobs/{job_id}/logs"

        with requests.get(url, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        if "log" in data:
                            yield data["log"]
                        elif "status" in data:
                            break

    async def connect_websocket(self):
        """Connect via WebSocket for real-time updates.

        Returns:
            WebSocket connection
        """
        return await websockets.connect(self.ws_url)


class WarpAIInterface:
    """High-level interface for Warp Terminal AI to use."""

    def __init__(self, client: Optional[WarpEngineClient] = None):
        """Initialize the AI interface.

        Args:
            client: WarpEngineClient instance (creates default if not provided)
        """
        self.client = client or WarpEngineClient()

    def process_user_request(self, request: str) -> str:
        """Process a natural language request from the user.

        Args:
            request: User's natural language request

        Returns:
            Response to show the user
        """
        # Parse the request to determine action
        request_lower = request.lower()

        if "create" in request_lower and "agent" in request_lower:
            return self._handle_agent_creation(request)
        elif "list" in request_lower and "agent" in request_lower:
            return self._handle_list_agents()
        elif "run" in request_lower:
            return self._handle_run_agent(request)
        else:
            return self._handle_generic(request)

    def _handle_agent_creation(self, request: str) -> str:
        """Handle agent creation request.

        Args:
            request: User request

        Returns:
            Response message
        """
        # Extract details from request (simplified for demo)
        if "research" in request.lower():
            agent_type = "RESEARCH"
            name = self._extract_topic(request) + " Research Expert"
        elif "code" in request.lower() or "build" in request.lower():
            agent_type = "CODE_GENERATOR"
            name = self._extract_topic(request) + " Code Generator"
        else:
            agent_type = "CUSTOM"
            name = self._extract_topic(request) + " Agent"

        description = f"Agent created from request: {request}"

        # Create the agent
        result = self.client.create_agent(
            name=name, agent_type=agent_type, description=description
        )

        if result.success:
            agent_info = result.result
            return f"""✅ Created agent: {agent_info['agent']['name']}
Slug: {agent_info['slug']}
Executable: {agent_info['executable']}

You can now run it with:
    echo "your input" | {agent_info['executable']}"""
        else:
            return f"❌ Failed to create agent: {result.error}"

    def _handle_list_agents(self) -> str:
        """Handle list agents request.

        Returns:
            List of agents
        """
        agents = self.client.list_agents()

        if not agents:
            return "No agents found. Create one with: 'create an agent that...'"

        response = "📋 Available Agents:\n"
        for agent in agents:
            response += f"  • {agent['name']} ({agent['slug']})\n"
            response += f"    {agent.get('description', 'No description')}\n"

        return response

    def _handle_run_agent(self, request: str) -> str:
        """Handle run agent request.

        Args:
            request: User request

        Returns:
            Agent output
        """
        # Extract agent name and input (simplified)
        agents = self.client.list_agents()
        if not agents:
            return "No agents available. Create one first."

        # Use first agent for demo
        agent = agents[0]
        input_text = request.replace("run", "").strip()

        result = self.client.run_agent(agent["slug"], input_text)

        if result.success:
            return f"Agent Output:\n{result.result.get('output', 'No output')}"
        else:
            return f"❌ Failed to run agent: {result.error}"

    def _handle_generic(self, request: str) -> str:
        """Handle generic request.

        Args:
            request: User request

        Returns:
            Help message
        """
        return """I can help you with:
• Create an agent: "Create an agent that researches quantum computing"
• List agents: "Show me all agents"
• Run an agent: "Run the research agent on climate change"

Service status: """ + (
            "✅ Running" if self.client.is_running() else "❌ Not running"
        )

    def _extract_topic(self, request: str) -> str:
        """Extract topic from request.

        Args:
            request: User request

        Returns:
            Extracted topic
        """
        # Simple extraction (would be more sophisticated in production)
        words = request.split()

        # Look for "about", "for", "that" as markers
        markers = ["about", "for", "that"]
        for i, word in enumerate(words):
            if word in markers and i + 1 < len(words):
                return " ".join(words[i + 1 : i + 3]).title()

        return "Custom"
