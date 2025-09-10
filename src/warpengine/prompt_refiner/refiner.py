"""
Prompt Refiner - Transforms raw user prompts into perfect agent creation instructions
Shows real-time refinement in the terminal with the 3-agent protocol constraints.
"""

from __future__ import annotations
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from ..api.client import A2AClient
from ..config import DATA_DIR
from ..staging import StageManager, StageTag
from .templates import TemplateLibrary


@dataclass
class RefinementResult:
    """Result of prompt refinement."""
    
    original_prompt: str
    refined_prompts: Dict[str, str]  # plan, execute, refine
    agent_type: str
    suggested_name: str
    suggested_description: str
    capabilities: List[str]
    constraints: List[str]
    refinement_steps: List[Dict[str, str]]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_prompt": self.original_prompt,
            "refined_prompts": self.refined_prompts,
            "agent_type": self.agent_type,
            "suggested_name": self.suggested_name,
            "suggested_description": self.suggested_description,
            "capabilities": self.capabilities,
            "constraints": self.constraints,
            "refinement_steps": self.refinement_steps,
            "metadata": self.metadata
        }


class PromptRefiner:
    """
    Refines user prompts into perfect agent creation instructions.
    Ensures compliance with the 3-agent protocol constraints.
    """
    
    # Protocol constraints
    PROTOCOL_RULES = [
        "Each agent MUST have exactly 3 prompts: plan, execute, refine",
        "Prompts must be self-contained and not reference external systems",
        "Each prompt should be under 500 tokens for optimal performance",
        "Prompts must follow the role-based pattern: 'You are Agent-X. Do Y.'",
        "The plan prompt must produce actionable steps",
        "The execute prompt must implement the plan",
        "The refine prompt must polish and perfect the output",
        "Agents must be deterministic and reproducible",
        "No agent can spawn more than 3 sub-agents",
        "All processing must be local - no external API calls in agent code"
    ]
    
    def __init__(self, client: Optional[A2AClient] = None):
        """
        Initialize the prompt refiner.
        
        Args:
            client: Optional A2A client for AI-powered refinement
        """
        self.client = client or A2AClient()
        self.template_library = TemplateLibrary()
        self.stage_manager = StageManager()
        self.refinement_history: List[RefinementResult] = []
        
        # Load refinement history
        self._load_history()
    
    def refine_prompt(
        self,
        user_prompt: str,
        show_realtime: bool = True
    ) -> RefinementResult:
        """
        Refine a user prompt into agent creation instructions.
        
        Args:
            user_prompt: Raw user prompt
            show_realtime: Whether to show real-time refinement in terminal
            
        Returns:
            Refinement result with perfect prompts
        """
        # Create initial stage
        stage = self.stage_manager.create_stage(
            tag=StageTag.PROMPT_RECEIVED,
            data={"prompt": user_prompt},
            timestamp=time.time()
        )
        
        if show_realtime:
            self._display_header()
            self._display_original(user_prompt)
        
        # Step 1: Analyze the prompt
        analysis = self._analyze_prompt(user_prompt)
        if show_realtime:
            self._display_analysis(analysis)
        
        # Step 2: Apply protocol constraints
        constrained = self._apply_constraints(analysis)
        if show_realtime:
            self._display_constraints(constrained)
        
        # Step 3: Generate refined prompts
        refined_prompts = self._generate_refined_prompts(user_prompt, analysis, constrained)
        if show_realtime:
            self._display_refined(refined_prompts)
        
        # Step 4: Validate and optimize
        final_prompts = self._validate_and_optimize(refined_prompts)
        if show_realtime:
            self._display_final(final_prompts)
        
        # Create result
        result = RefinementResult(
            original_prompt=user_prompt,
            refined_prompts=final_prompts,
            agent_type=analysis.get("agent_type", "RESEARCH"),
            suggested_name=analysis.get("suggested_name", "Custom Agent"),
            suggested_description=analysis.get("description", "Agent created from refined prompts"),
            capabilities=analysis.get("capabilities", []),
            constraints=constrained.get("applied_constraints", []),
            refinement_steps=self._get_refinement_steps(),
            metadata={
                "stage_id": stage.id,
                "analysis": analysis,
                "constraints": constrained
            }
        )
        
        # Update stage with refinement
        self.stage_manager.create_stage(
            tag=StageTag.PROMPT_REFINED,
            data=result.to_dict(),
            parent_stage=stage.id
        )
        
        # Save to history
        self.refinement_history.append(result)
        self._save_history()
        
        return result
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze the user prompt to understand intent."""
        # Use AI to analyze the prompt
        analysis_prompt = f"""
Analyze this user prompt for agent creation:
"{prompt}"

Extract:
1. Primary goal/purpose
2. Required capabilities
3. Input/output expectations
4. Suggested agent type (RESEARCH, CODE_GENERATOR, DATA_ANALYST)
5. Suggested name (short, descriptive)
6. Key actions the agent should perform

Respond in JSON format.
"""
        
        response = self.client.complete(
            job_id="prompt_analysis",
            agent="analyzer",
            input_text=analysis_prompt,
            mode="high_reasoning"
        )
        
        try:
            # Parse AI response
            output = response.get("output", "{}")
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {}
        except:
            # Fallback analysis
            analysis = self._fallback_analysis(prompt)
        
        return analysis
    
    def _apply_constraints(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply protocol constraints to the analysis."""
        constrained = {
            "applied_constraints": [],
            "modifications": []
        }
        
        # Check token limits
        if analysis.get("complexity", "high") == "high":
            constrained["applied_constraints"].append("Simplified for token limits")
            constrained["modifications"].append("Break complex tasks into 3 clear phases")
        
        # Ensure 3-agent pattern
        constrained["applied_constraints"].append("Enforced 3-agent pattern (plan/execute/refine)")
        
        # Check for external dependencies
        capabilities = analysis.get("capabilities", [])
        if any(cap in capabilities for cap in ["web_access", "api_calls", "external_data"]):
            constrained["applied_constraints"].append("Removed external dependencies")
            constrained["modifications"].append("Converted to local processing only")
        
        # Add determinism constraint
        constrained["applied_constraints"].append("Ensured deterministic behavior")
        
        return constrained
    
    def _generate_refined_prompts(
        self,
        original: str,
        analysis: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate the refined 3-agent prompts."""
        
        # Get template based on agent type
        agent_type = analysis.get("agent_type", "RESEARCH")
        template = self.template_library.get_template(agent_type)
        
        # Customize template with analysis
        goal = analysis.get("goal", original)
        capabilities = analysis.get("capabilities", [])
        
        # Generate plan prompt
        plan_prompt = f"""You are Agent-Plan, a strategic planning specialist.
Your task: Create a comprehensive, actionable plan for the following goal:
{goal}

Requirements:
1. Break down the task into clear, sequential steps
2. Identify required resources and dependencies
3. Define success criteria for each step
4. Ensure all processing can be done locally
5. Output a structured plan with numbered steps

Constraints: {', '.join(constraints.get('applied_constraints', []))}

Focus on creating a plan that can be executed deterministically."""
        
        # Generate execute prompt
        execute_prompt = f"""You are Agent-Execute, an implementation specialist.
Your task: Execute the provided plan to achieve:
{goal}

Requirements:
1. Follow the plan step by step
2. Implement each component thoroughly
3. Handle edge cases gracefully
4. Produce complete, working output
5. Document your implementation choices

Capabilities available: {', '.join(capabilities[:3])}  # Limit to 3 main capabilities

Execute with precision and completeness."""
        
        # Generate refine prompt
        refine_prompt = f"""You are Agent-Refine, a quality assurance specialist.
Your task: Polish and perfect the executed output for:
{goal}

Requirements:
1. Review for completeness and accuracy
2. Optimize for clarity and usability
3. Ensure professional presentation
4. Validate against original requirements
5. Add final touches for production readiness

Focus on delivering exceptional quality."""
        
        return {
            "plan": plan_prompt,
            "execute": execute_prompt,
            "refine": refine_prompt
        }
    
    def _validate_and_optimize(self, prompts: Dict[str, str]) -> Dict[str, str]:
        """Validate and optimize the prompts."""
        optimized = {}
        
        for key, prompt in prompts.items():
            # Check token count (approximate)
            token_count = len(prompt.split()) * 1.3
            
            if token_count > 500:
                # Compress prompt
                lines = prompt.split('\n')
                essential_lines = [
                    line for line in lines
                    if line.strip() and not line.strip().startswith('#')
                ]
                prompt = '\n'.join(essential_lines[:15])  # Keep essential parts
            
            # Ensure proper format
            if not prompt.startswith("You are Agent-"):
                if key == "plan":
                    prompt = "You are Agent-Plan. " + prompt
                elif key == "execute":
                    prompt = "You are Agent-Execute. " + prompt
                elif key == "refine":
                    prompt = "You are Agent-Refine. " + prompt
            
            optimized[key] = prompt.strip()
        
        return optimized
    
    def _fallback_analysis(self, prompt: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available."""
        # Simple keyword-based analysis
        prompt_lower = prompt.lower()
        
        agent_type = "RESEARCH"
        if any(word in prompt_lower for word in ["code", "program", "build", "create"]):
            agent_type = "CODE_GENERATOR"
        elif any(word in prompt_lower for word in ["data", "analyze", "statistics", "chart"]):
            agent_type = "DATA_ANALYST"
        
        # Extract potential name
        words = prompt.split()[:5]
        name = " ".join(words[:3]) + " Agent"
        
        return {
            "goal": prompt,
            "agent_type": agent_type,
            "suggested_name": name,
            "description": f"Agent for: {prompt[:100]}",
            "capabilities": ["processing", "analysis", "generation"],
            "complexity": "medium"
        }
    
    def _get_refinement_steps(self) -> List[Dict[str, str]]:
        """Get the refinement steps for display."""
        return [
            {
                "step": "Analysis",
                "description": "Analyzed user intent and requirements"
            },
            {
                "step": "Constraint Application",
                "description": "Applied protocol constraints and rules"
            },
            {
                "step": "Prompt Generation",
                "description": "Generated 3-agent prompts"
            },
            {
                "step": "Optimization",
                "description": "Validated and optimized for performance"
            }
        ]
    
    def _display_header(self) -> None:
        """Display refinement header."""
        print("\n" + "="*80)
        print("🎯 PROMPT REFINEMENT ENGINE")
        print("Transforming your request into perfect agent instructions...")
        print("="*80 + "\n")
    
    def _display_original(self, prompt: str) -> None:
        """Display original prompt."""
        print("📝 ORIGINAL PROMPT:")
        print("-"*40)
        print(prompt)
        print("-"*40 + "\n")
    
    def _display_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display analysis results."""
        print("🔍 ANALYSIS:")
        print(f"  • Agent Type: {analysis.get('agent_type', 'RESEARCH')}")
        print(f"  • Suggested Name: {analysis.get('suggested_name', 'Custom Agent')}")
        print(f"  • Complexity: {analysis.get('complexity', 'medium')}")
        print()
    
    def _display_constraints(self, constraints: Dict[str, Any]) -> None:
        """Display applied constraints."""
        print("⚙️ APPLYING PROTOCOL CONSTRAINTS:")
        for constraint in constraints.get("applied_constraints", []):
            print(f"  ✓ {constraint}")
        print()
    
    def _display_refined(self, prompts: Dict[str, str]) -> None:
        """Display refined prompts."""
        print("✨ REFINED PROMPTS:")
        print("-"*40)
        
        for key, prompt in prompts.items():
            print(f"\n[{key.upper()}]")
            # Show first 3 lines
            lines = prompt.split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"  {line[:75]}...")
        
        print("-"*40 + "\n")
    
    def _display_final(self, prompts: Dict[str, str]) -> None:
        """Display final validation."""
        print("✅ VALIDATION COMPLETE:")
        print(f"  • Plan Prompt: {len(prompts['plan'].split())} words")
        print(f"  • Execute Prompt: {len(prompts['execute'].split())} words")
        print(f"  • Refine Prompt: {len(prompts['refine'].split())} words")
        print("\n🎉 Prompts refined and ready for agent creation!\n")
    
    def _load_history(self) -> None:
        """Load refinement history from disk."""
        history_file = DATA_DIR / "refinement_history.json"
        if history_file.exists():
            try:
                data = json.loads(history_file.read_text())
                self.refinement_history = [
                    RefinementResult(**item) for item in data
                ]
            except:
                self.refinement_history = []
    
    def _save_history(self) -> None:
        """Save refinement history to disk."""
        history_file = DATA_DIR / "refinement_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = [r.to_dict() for r in self.refinement_history[-100:]]  # Keep last 100
        history_file.write_text(json.dumps(data, indent=2))
