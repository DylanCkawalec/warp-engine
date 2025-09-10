"""Enhanced Agent Generator with Templates and Lifecycle Management."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..config import AGENTS_ROOT, BIN_DIR, PROJECT_ROOT
from ..registry.registry import upsert_agent, get_agent
from ..api.client import A2AClient
from ..warp_integration.warp_client import WarpTerminalClient, WarpProfile, WarpWorkflow


class AgentType(Enum):
    """Agent type enumeration."""

    RESEARCH = "research"
    CODE_GENERATOR = "code_generator"
    DATA_ANALYST = "data_analyst"
    CUSTOM = "custom"


@dataclass
class AgentTemplate:
    """Agent template configuration."""

    name: str
    description: str
    type: AgentType
    prompts: Dict[str, str]
    capabilities: List[str]
    requirements: List[str]
    test_cases: List[Dict[str, Any]]


class EnhancedAgentBuilder:
    """Enhanced agent builder with lifecycle management."""

    # Pre-defined templates
    TEMPLATES = {
        AgentType.RESEARCH: AgentTemplate(
            name="Research Agent",
            description="Deep research with multi-page expert output",
            type=AgentType.RESEARCH,
            prompts={
                "plan": "You are a research planner. Create a comprehensive research outline with sources, methodologies, and expected outcomes. Include: 1) Research questions, 2) Data sources, 3) Analysis methods, 4) Expected deliverables.",
                "execute": "You are a research executor. Gather information, analyze data, and produce a detailed multi-page report with citations. Structure: Executive Summary, Introduction, Methodology, Findings, Analysis, Conclusions, References.",
                "refine": "You are a research editor. Polish the report for clarity, accuracy, and professional presentation. Ensure proper citations, consistent formatting, and logical flow.",
            },
            capabilities=[
                "web_search",
                "document_analysis",
                "citation_management",
                "report_generation",
            ],
            requirements=["openai", "beautifulsoup4", "scholarly", "pypdf2"],
            test_cases=[
                {
                    "input": "Research the impact of AI on healthcare",
                    "expected_sections": [
                        "Executive Summary",
                        "Introduction",
                        "Findings",
                    ],
                }
            ],
        ),
        AgentType.CODE_GENERATOR: AgentTemplate(
            name="Code Generation Agent",
            description="Generate production-ready code with tests",
            type=AgentType.CODE_GENERATOR,
            prompts={
                "plan": "You are a software architect. Design the solution architecture, identify components, and plan the implementation. Include: 1) System design, 2) Component breakdown, 3) API contracts, 4) Testing strategy.",
                "execute": "You are a senior developer. Implement the solution with clean code, proper error handling, and documentation. Follow best practices, add type hints, include docstrings, and ensure modularity.",
                "refine": "You are a code reviewer. Optimize performance, ensure best practices, and add comprehensive tests. Check for security issues, improve readability, and validate edge cases.",
            },
            capabilities=["code_generation", "testing", "documentation", "linting"],
            requirements=["black", "pytest", "mypy", "ruff"],
            test_cases=[
                {
                    "input": "Create a REST API for user management",
                    "expected_files": ["api.py", "models.py", "test_api.py"],
                }
            ],
        ),
        AgentType.DATA_ANALYST: AgentTemplate(
            name="Data Analysis Agent",
            description="Analyze data and produce insights",
            type=AgentType.DATA_ANALYST,
            prompts={
                "plan": "You are a data scientist. Plan the analysis approach, identify metrics, and design visualizations. Include: 1) Data exploration strategy, 2) Statistical methods, 3) Visualization types, 4) Insight extraction plan.",
                "execute": "You are a data analyst. Process the data, perform statistical analysis, and generate insights. Create visualizations, calculate metrics, identify patterns, and test hypotheses.",
                "refine": "You are a data storyteller. Create compelling narratives and actionable recommendations from the analysis. Ensure clarity, highlight key findings, and provide business context.",
            },
            capabilities=[
                "data_processing",
                "statistical_analysis",
                "visualization",
                "reporting",
            ],
            requirements=["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"],
            test_cases=[
                {
                    "input": "Analyze sales data trends",
                    "expected_outputs": ["charts", "metrics", "recommendations"],
                }
            ],
        ),
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the enhanced agent builder.

        Args:
            config_path: Path to config.api.json
        """
        self.config_path = config_path or PROJECT_ROOT / "config.api.json"
        self.config = self._load_config()
        self.warp_client = None

        # Try to initialize Warp client
        try:
            self.warp_client = WarpTerminalClient()
        except Exception:
            pass

        # Ensure directories exist
        self._ensure_directories()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.api.json.

        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {}

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        AGENTS_ROOT.mkdir(parents=True, exist_ok=True)
        BIN_DIR.mkdir(parents=True, exist_ok=True)

        # Create additional directories from config
        paths = self.config.get("paths", {})
        for path_key, path_value in paths.items():
            Path(path_value).mkdir(parents=True, exist_ok=True)

    def interactive_agent_creation(self) -> str:
        """Interactive agent creation with template selection.

        Returns:
            Agent slug
        """
        print("\n🚀 Welcome to Warp Engine Agent Builder!\n")
        print("Choose an agent type:\n")
        print("1. 🔬 Research Agent - Deep research with multi-page expert output")
        print("2. 💻 Code Generator - Generate production-ready code with tests")
        print("3. 📊 Data Analyst - Analyze data and produce insights")
        print("4. 🎨 Custom Agent - Create your own agent from scratch\n")

        choice = input("Select (1-4): ").strip()

        if choice == "1":
            agent_type = AgentType.RESEARCH
        elif choice == "2":
            agent_type = AgentType.CODE_GENERATOR
        elif choice == "3":
            agent_type = AgentType.DATA_ANALYST
        else:
            agent_type = AgentType.CUSTOM

        if agent_type != AgentType.CUSTOM:
            template = self.TEMPLATES[agent_type]
            print(f"\n✅ Selected: {template.name}")

            # Get custom name
            custom_name = input(f"\nAgent name (default: {template.name}): ").strip()
            if not custom_name:
                custom_name = template.name

            # Get custom description
            print(f"\nDefault description: {template.description}")
            custom_desc = input(
                "Custom description (press Enter to use default): "
            ).strip()
            if not custom_desc:
                custom_desc = template.description

            # Option to customize prompts
            customize = input("\nCustomize prompts? (y/N): ").strip().lower()

            if customize == "y":
                prompts = {}
                for prompt_type in ["plan", "execute", "refine"]:
                    print(f"\nDefault {prompt_type} prompt:")
                    print(f"  {template.prompts[prompt_type][:100]}...")
                    custom_prompt = input(
                        f"Custom {prompt_type} prompt (Enter to use default): "
                    ).strip()
                    prompts[prompt_type] = (
                        custom_prompt
                        if custom_prompt
                        else template.prompts[prompt_type]
                    )
            else:
                prompts = template.prompts

            # Create the agent
            return self.create_agent_from_template(
                agent_type=agent_type,
                name=custom_name,
                description=custom_desc,
                prompts=prompts,
            )
        else:
            # Custom agent creation
            name = input("\nAgent name: ").strip()
            description = input("Description: ").strip()

            print("\nDefine the three agent prompts:")
            plan_prompt = (
                input("Plan prompt: ").strip()
                or "You are Agent-Plan. Produce a comprehensive plan."
            )
            exec_prompt = (
                input("Execute prompt: ").strip()
                or "You are Agent-Exec. Execute the plan thoroughly."
            )
            refine_prompt = (
                input("Refine prompt: ").strip()
                or "You are Agent-Refine. Polish and perfect the output."
            )

            return self.create_custom_agent(
                name=name,
                description=description,
                prompts={
                    "plan": plan_prompt,
                    "execute": exec_prompt,
                    "refine": refine_prompt,
                },
            )

    def create_agent_from_template(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        prompts: Dict[str, str],
    ) -> str:
        """Create an agent from a template.

        Args:
            agent_type: Type of agent
            name: Agent name
            description: Agent description
            prompts: Agent prompts

        Returns:
            Agent slug
        """
        template = self.TEMPLATES.get(agent_type)
        if not template:
            raise ValueError(f"Unknown agent type: {agent_type}")

        slug = self._slugify(name)
        agent_dir = AGENTS_ROOT / slug
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        (agent_dir / "__init__.py").write_text("")

        # Create runner.py with enhanced functionality
        runner_code = self._generate_runner_code(
            prompts=prompts, capabilities=template.capabilities, agent_type=agent_type
        )
        (agent_dir / "runner.py").write_text(runner_code)

        # Create test file
        test_code = self._generate_test_code(slug, template.test_cases)
        (agent_dir / f"test_{slug}.py").write_text(test_code)

        # Create requirements.txt
        requirements = template.requirements + ["openai", "requests"]
        (agent_dir / "requirements.txt").write_text("\n".join(requirements))

        # Update registry
        upsert_agent(
            {
                "name": name,
                "slug": slug,
                "description": description,
                "type": agent_type.value,
                "entry": f"warpengine.agents.{slug}.runner:run",
                "prompts": prompts,
                "capabilities": template.capabilities,
                "requirements": template.requirements,
                "status": "active",
            }
        )

        # Create executable shim
        shim_path = self._create_executable_shim(slug)

        # Create Warp profile if available
        if self.warp_client:
            profile = WarpProfile(
                id=f"warp-engine-{slug}",
                name=name,
                permissions=["read", "write", "execute"],
                context_sources=["codebase", "web", "documentation"],
                model="gpt-4-turbo-preview",
            )
            self.warp_client.create_agent_profile(profile)

            # Create Warp workflow
            workflow = WarpWorkflow(
                name=f"run-{slug}",
                description=f"Run {name} agent",
                commands=[
                    f"cd {PROJECT_ROOT}",
                    f"source .venv/bin/activate",
                    f"{shim_path}",
                ],
                variables={},
            )
            self.warp_client.create_workflow(workflow)

        # Run initial tests
        print(f"\n🧪 Running tests for {name}...")
        test_passed = self._run_tests(slug)

        if test_passed:
            print(f"✅ Agent '{name}' created successfully!")
            print(f"📦 Slug: {slug}")
            print(f"🚀 Run with: {shim_path}")
            print(f"🔧 Or: warp-engine agent run --name {slug}")

            if self.warp_client:
                print(f"🎯 Warp profile: warp-engine-{slug}")
                print(f"📋 Warp workflow: run-{slug}")
        else:
            print(f"⚠️ Agent created but tests failed. Please review and fix.")

        return slug

    def create_custom_agent(
        self, name: str, description: str, prompts: Dict[str, str]
    ) -> str:
        """Create a custom agent.

        Args:
            name: Agent name
            description: Agent description
            prompts: Agent prompts

        Returns:
            Agent slug
        """
        slug = self._slugify(name)
        agent_dir = AGENTS_ROOT / slug
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        (agent_dir / "__init__.py").write_text("")

        # Create runner.py
        runner_code = self._generate_runner_code(prompts)
        (agent_dir / "runner.py").write_text(runner_code)

        # Update registry
        upsert_agent(
            {
                "name": name,
                "slug": slug,
                "description": description,
                "type": "custom",
                "entry": f"warpengine.agents.{slug}.runner:run",
                "prompts": prompts,
                "status": "active",
            }
        )

        # Create executable shim
        shim_path = self._create_executable_shim(slug)

        print(f"\n✅ Custom agent '{name}' created!")
        print(f"📦 Slug: {slug}")
        print(f"🚀 Run with: {shim_path}")

        return slug

    def _slugify(self, name: str) -> str:
        """Convert name to slug.

        Args:
            name: Agent name

        Returns:
            Slug
        """
        s = name.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "_", s)
        s = re.sub(r"^_+|_+$", "", s)
        return s or "agent"

    def _generate_runner_code(
        self,
        prompts: Dict[str, str],
        capabilities: Optional[List[str]] = None,
        agent_type: Optional[AgentType] = None,
    ) -> str:
        """Generate runner.py code.

        Args:
            prompts: Agent prompts
            capabilities: Agent capabilities
            agent_type: Agent type

        Returns:
            Python code
        """
        capabilities_str = str(capabilities) if capabilities else "[]"

        code = f'''"""Agent runner module."""

from __future__ import annotations
import json
import time
from typing import Tuple, Dict, Any, Optional
from pathlib import Path

from warpengine.orchestrator.chain import run_three_agent_workflow
from warpengine.storage.cache import new_job_id, put_record

PROMPTS = {{
    "plan": {prompts['plan']!r},
    "execute": {prompts['execute']!r},
    "refine": {prompts['refine']!r}
}}

CAPABILITIES = {capabilities_str}

def run(text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    """Run the agent workflow.
    
    Args:
        text: Input text
        context: Optional context
    
    Returns:
        Tuple of (job_id, final_output)
    """
    # Add context to prompts if provided
    prompts = PROMPTS.copy()
    if context:
        for key, value in prompts.items():
            prompts[key] = f"{{value}}\\n\\nContext: {{json.dumps(context)}}"
    
    # Run the three-agent workflow
    job_id, final_output = run_three_agent_workflow(text, prompts)
    
    # Log execution
    _log_execution(job_id, text, final_output)
    
    return job_id, final_output

def _log_execution(job_id: str, input_text: str, output_text: str) -> None:
    """Log agent execution.
    
    Args:
        job_id: Job ID
        input_text: Input text
        output_text: Output text
    """
    log_dir = Path.home() / ".warp-engine" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{{job_id}}.json"
    log_data = {{
        "job_id": job_id,
        "timestamp": time.time(),
        "input_length": len(input_text),
        "output_length": len(output_text),
        "capabilities": CAPABILITIES
    }}
    
    try:
        log_file.write_text(json.dumps(log_data, indent=2))
    except Exception:
        pass
'''

        # Add specialized code for specific agent types
        if agent_type == AgentType.RESEARCH:
            code += '''

def generate_report(text: str) -> str:
    """Generate a research report.
    
    Args:
        text: Research topic
    
    Returns:
        Formatted report
    """
    job_id, output = run(text)
    
    # Format as a proper report
    sections = ["Executive Summary", "Introduction", "Methodology", "Findings", "Conclusions"]
    formatted = f"# Research Report: {text}\\n\\n"
    
    for section in sections:
        if section.lower() in output.lower():
            formatted += f"## {section}\\n\\n"
    
    formatted += output
    return formatted
'''

        return code

    def _generate_test_code(self, slug: str, test_cases: List[Dict[str, Any]]) -> str:
        """Generate test code.

        Args:
            slug: Agent slug
            test_cases: Test cases

        Returns:
            Test code
        """
        test_code = f'''"""Tests for {slug} agent."""

import pytest
from warpengine.agents.{slug}.runner import run

def test_agent_basic():
    """Test basic agent functionality."""
    job_id, output = run("Test input")
    assert job_id
    assert output
    assert len(output) > 0

'''

        for i, test_case in enumerate(test_cases):
            test_code += f'''
def test_agent_case_{i+1}():
    """Test case {i+1}: {test_case.get('input', 'Test')}"""
    job_id, output = run("{test_case.get('input', 'Test input')}")
    assert job_id
    assert output
'''

            if "expected_sections" in test_case:
                for section in test_case["expected_sections"]:
                    test_code += f'    assert "{section}" in output\n'

            if "expected_outputs" in test_case:
                for expected in test_case["expected_outputs"]:
                    test_code += f"    # Check for {expected}\n"

        return test_code

    def _create_executable_shim(self, slug: str) -> Path:
        """Create executable shim.

        Args:
            slug: Agent slug

        Returns:
            Path to shim
        """
        shim = BIN_DIR / slug
        content = f'''#!/usr/bin/env python3
"""Executable shim for {slug} agent."""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "src"))

from warpengine.agents.{slug}.runner import run

def main():
    """Main entry point."""
    print("🤖 Warp Engine Agent: {slug}")
    print("=" * 50)
    print("Enter your input (Ctrl+D when done):\\n")
    
    try:
        text = sys.stdin.read()
        if not text.strip():
            print("No input provided.")
            sys.exit(1)
        
        print("\\n🔄 Processing...")
        job_id, output = run(text)
        
        print("\\n✅ Output:")
        print("=" * 50)
        print(output)
        print("=" * 50)
        print(f"\\n📋 Job ID: {{job_id}}")
        
    except KeyboardInterrupt:
        print("\\n❌ Cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        shim.write_text(content)
        os.chmod(shim, 0o755)
        return shim

    def _run_tests(self, slug: str) -> bool:
        """Run tests for an agent.

        Args:
            slug: Agent slug

        Returns:
            True if tests pass
        """
        test_file = AGENTS_ROOT / slug / f"test_{slug}.py"
        if not test_file.exists():
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-q"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False
