"""Warp Terminal Client for agent integration."""

from __future__ import annotations

import json
import subprocess
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..config import env


@dataclass
class WarpProfile:
    """Warp agent profile configuration."""

    id: str
    name: str
    permissions: List[str]
    context_sources: List[str]
    model: str = "gpt-4-turbo-preview"


@dataclass
class WarpWorkflow:
    """Warp workflow configuration."""

    name: str
    description: str
    commands: List[str]
    variables: Dict[str, str]


class WarpTerminalClient:
    """Client for interacting with Warp terminal."""

    def __init__(self, cli_path: Optional[str] = None):
        """Initialize Warp terminal client.

        Args:
            cli_path: Path to warp CLI (defaults to searching PATH)
        """
        self.cli_path = cli_path or self._find_warp_cli()
        if not self.cli_path:
            raise RuntimeError("Warp CLI not found. Please install Warp terminal.")

        # Check if Warp is available
        self.available = self._check_availability()

    def _find_warp_cli(self) -> Optional[str]:
        """Find the Warp CLI executable.

        Returns:
            Path to warp CLI or None if not found
        """
        # Check common locations
        common_paths = [
            "/usr/local/bin/warp",
            "/opt/homebrew/bin/warp",
            "/usr/bin/warp",
            os.path.expanduser("~/bin/warp"),
            os.path.expanduser("~/.warp/bin/warp"),
        ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # Try to find in PATH
        warp_path = shutil.which("warp")
        if warp_path:
            return warp_path

        # Try warp-dev as fallback
        warp_dev = shutil.which("warp-dev")
        if warp_dev:
            return warp_dev

        return None

    def _check_availability(self) -> bool:
        """Check if Warp CLI is available and working.

        Returns:
            True if Warp is available
        """
        try:
            result = subprocess.run(
                [self.cli_path, "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def run_command(
        self, command: str, cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """Run a command in Warp terminal.

        Args:
            command: Command to execute
            cwd: Working directory

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def create_agent_profile(self, profile: WarpProfile) -> bool:
        """Create a Warp agent profile.

        Args:
            profile: Agent profile configuration

        Returns:
            True if successful
        """
        # Warp doesn't have a direct API for this yet
        # This would integrate with Warp's profile system
        # For now, we'll store profiles locally
        profiles_dir = Path.home() / ".warp" / "agent_profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)

        profile_file = profiles_dir / f"{profile.id}.json"
        profile_data = {
            "id": profile.id,
            "name": profile.name,
            "permissions": profile.permissions,
            "context_sources": profile.context_sources,
            "model": profile.model,
        }

        try:
            profile_file.write_text(json.dumps(profile_data, indent=2))
            return True
        except Exception:
            return False

    def run_agent(
        self,
        prompt: str,
        profile_id: Optional[str] = None,
        context_files: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Run a Warp agent with a prompt.

        Args:
            prompt: The prompt to send to the agent
            profile_id: Optional profile ID to use
            context_files: Optional list of files to include as context

        Returns:
            Tuple of (success, output)
        """
        # Build the warp agent command
        cmd_parts = [self.cli_path, "agent", "run"]

        # Add profile if specified
        if profile_id:
            cmd_parts.extend(["--profile", profile_id])

        # Add prompt
        cmd_parts.extend(["--prompt", json.dumps(prompt)])

        # Add context files
        if context_files:
            for file in context_files:
                cmd_parts.extend(["--context", file])

        try:
            result = subprocess.run(
                cmd_parts, capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)

    def create_workflow(self, workflow: WarpWorkflow) -> bool:
        """Create a Warp workflow.

        Args:
            workflow: Workflow configuration

        Returns:
            True if successful
        """
        # Create workflow YAML
        workflow_dir = Path.home() / ".warp" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflow_dir / f"{workflow.name}.yaml"

        # Build YAML content
        yaml_content = f"""name: {workflow.name}
description: {workflow.description}
"""

        if workflow.variables:
            yaml_content += "variables:\n"
            for key, value in workflow.variables.items():
                yaml_content += f"  {key}: {value}\n"

        yaml_content += "commands:\n"
        for cmd in workflow.commands:
            yaml_content += f"  - {cmd}\n"

        try:
            workflow_file.write_text(yaml_content)
            return True
        except Exception:
            return False

    def list_agents(self) -> List[Dict[str, Any]]:
        """List available Warp agents.

        Returns:
            List of agent configurations
        """
        try:
            result = subprocess.run(
                [self.cli_path, "agent", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Parse the output (assuming JSON format)
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Fallback to line parsing
                    agents = []
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            agents.append({"name": line.strip()})
                    return agents
            return []
        except Exception:
            return []

    def get_agent_profiles(self) -> List[str]:
        """Get list of available agent profiles.

        Returns:
            List of profile IDs
        """
        try:
            result = subprocess.run(
                [self.cli_path, "agent", "profile", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                profiles = []
                for line in result.stdout.strip().split("\n"):
                    if line and not line.startswith("Use the"):
                        # Extract profile ID from line
                        parts = line.split()
                        if parts:
                            profiles.append(parts[0])
                return profiles
            return []
        except Exception:
            return []

    def launch_terminal(
        self, command: Optional[str] = None, cwd: Optional[str] = None
    ) -> bool:
        """Launch Warp terminal with optional command.

        Args:
            command: Optional command to run on launch
            cwd: Optional working directory

        Returns:
            True if successful
        """
        cmd_parts = [self.cli_path]

        if command:
            cmd_parts.extend(["--command", command])

        if cwd:
            cmd_parts.extend(["--cwd", cwd])

        try:
            subprocess.Popen(cmd_parts)
            return True
        except Exception:
            return False

    def send_notification(self, title: str, message: str) -> bool:
        """Send a notification through Warp.

        Args:
            title: Notification title
            message: Notification message

        Returns:
            True if successful
        """
        # This would integrate with Warp's notification system
        # For now, use system notifications
        try:
            if os.uname().sysname == "Darwin":  # macOS
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{message}" with title "{title}"',
                    ]
                )
                return True
            return False
        except Exception:
            return False
