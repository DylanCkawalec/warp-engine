"""
Prompt Templates - Library of refined prompt patterns
Provides proven templates for different agent types.
"""

from __future__ import annotations
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A reusable prompt template."""
    
    name: str
    type: str
    plan_template: str
    execute_template: str
    refine_template: str
    variables: List[str]
    examples: List[Dict[str, str]]
    
    def fill(self, **kwargs) -> Dict[str, str]:
        """Fill the template with provided variables."""
        return {
            "plan": self.plan_template.format(**kwargs),
            "execute": self.execute_template.format(**kwargs),
            "refine": self.refine_template.format(**kwargs)
        }


class TemplateLibrary:
    """Library of refined prompt templates."""
    
    def __init__(self):
        """Initialize the template library."""
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, PromptTemplate]:
        """Load default templates."""
        return {
            "RESEARCH": PromptTemplate(
                name="Research Template",
                type="RESEARCH",
                plan_template="""You are Agent-Plan, a research strategist.
Create a comprehensive research plan for: {topic}

Your plan must include:
1. Research questions to answer
2. Information sources to consult
3. Analysis methodology
4. Expected deliverables
5. Quality criteria

Output a numbered, actionable plan.""",
                
                execute_template="""You are Agent-Execute, a research specialist.
Execute the research plan for: {topic}

Following the provided plan:
1. Gather relevant information
2. Analyze findings systematically
3. Synthesize insights
4. Create comprehensive documentation
5. Include citations and sources

Produce a detailed research output.""",
                
                refine_template="""You are Agent-Refine, a research editor.
Polish the research output for: {topic}

Your refinements:
1. Ensure accuracy and completeness
2. Improve clarity and readability
3. Verify citations and sources
4. Format professionally
5. Add executive summary

Deliver publication-ready research.""",
                
                variables=["topic"],
                examples=[
                    {"topic": "quantum computing applications"},
                    {"topic": "sustainable energy solutions"}
                ]
            ),
            
            "CODE_GENERATOR": PromptTemplate(
                name="Code Generation Template",
                type="CODE_GENERATOR",
                plan_template="""You are Agent-Plan, a software architect.
Design the architecture for: {feature}

Your plan must include:
1. Component breakdown
2. Data structures needed
3. Algorithm selection
4. Error handling strategy
5. Testing approach

Output a detailed technical plan.""",
                
                execute_template="""You are Agent-Execute, a senior developer.
Implement the solution for: {feature}

Following the architecture plan:
1. Write clean, modular code
2. Implement error handling
3. Add comprehensive comments
4. Include type hints
5. Follow best practices

Produce production-ready code.""",
                
                refine_template="""You are Agent-Refine, a code reviewer.
Optimize the code for: {feature}

Your improvements:
1. Enhance performance
2. Improve readability
3. Add missing tests
4. Ensure security
5. Complete documentation

Deliver exceptional code quality.""",
                
                variables=["feature"],
                examples=[
                    {"feature": "REST API with authentication"},
                    {"feature": "real-time data processing pipeline"}
                ]
            ),
            
            "DATA_ANALYST": PromptTemplate(
                name="Data Analysis Template",
                type="DATA_ANALYST",
                plan_template="""You are Agent-Plan, a data strategist.
Plan the analysis for: {dataset}

Your plan must include:
1. Data exploration strategy
2. Statistical methods to apply
3. Visualization types needed
4. Hypothesis to test
5. Insights to extract

Output a structured analysis plan.""",
                
                execute_template="""You are Agent-Execute, a data scientist.
Analyze the data for: {dataset}

Following the analysis plan:
1. Explore data characteristics
2. Apply statistical methods
3. Create visualizations
4. Test hypotheses
5. Extract insights

Produce comprehensive analysis results.""",
                
                refine_template="""You are Agent-Refine, a data storyteller.
Present the analysis for: {dataset}

Your presentation:
1. Highlight key findings
2. Create compelling narrative
3. Simplify complex insights
4. Add recommendations
5. Ensure accuracy

Deliver actionable insights.""",
                
                variables=["dataset"],
                examples=[
                    {"dataset": "customer behavior patterns"},
                    {"dataset": "market trend analysis"}
                ]
            )
        }
    
    def get_template(self, template_type: str) -> PromptTemplate:
        """Get a template by type."""
        return self.templates.get(
            template_type,
            self.templates["RESEARCH"]  # Default
        )
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a custom template."""
        self.templates[template.type] = template
    
    def list_templates(self) -> List[str]:
        """List available template types."""
        return list(self.templates.keys())
