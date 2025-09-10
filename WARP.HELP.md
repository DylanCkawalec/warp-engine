# 🤖 WARP.HELP - AI Agent Creation Protocol

## FOR AI AGENTS: How to Use Warp Engine

This document is designed for AI assistants (like Warp Terminal's AI) to understand how to autonomously create specialized agents using the Warp Engine protocol.

---

## CORE CONCEPT

Warp Engine is a **meta-agent factory**. When a user asks you to create an agent for a specific task, you can use Warp Engine to generate a specialized, persistent agent that handles that task perfectly.

**User says:** "Create an agent that researches quantum computing"
**You do:** Use Warp Engine to build that agent automatically

---

## QUICK REFERENCE - AGENT CREATION

### Pattern 1: Research Agent
**User Request Examples:**
- "I need deep research on [TOPIC]"
- "Create an expert that analyzes [SUBJECT]"
- "Build a research bot for [DOMAIN]"

**Your Action:**
```python
from warpengine.agent_builder.enhanced_generator import EnhancedAgentBuilder, AgentType

builder = EnhancedAgentBuilder()
slug = builder.create_agent_from_template(
    agent_type=AgentType.RESEARCH,
    name="{TOPIC} Research Expert",
    description="Deep research agent for {TOPIC}",
    prompts={
        "plan": "Create comprehensive research plan for {TOPIC} including methodology, sources, and deliverables",
        "execute": "Produce multi-page expert report with citations, analysis, and insights on {TOPIC}",
        "refine": "Polish for academic quality, ensure accuracy, format in LaTeX/Markdown"
    }
)
```

### Pattern 2: Code Generator
**User Request Examples:**
- "Build an agent that creates [TYPE] applications"
- "I need a bot that generates [LANGUAGE] code"
- "Make an AI that builds [FRAMEWORK] projects"

**Your Action:**
```python
slug = builder.create_agent_from_template(
    agent_type=AgentType.CODE_GENERATOR,
    name="{TYPE} Code Generator",
    description="Generates production-ready {TYPE} code",
    prompts={
        "plan": "Design architecture for {TYPE} solution, identify components and patterns",
        "execute": "Implement complete {TYPE} solution with tests and documentation",
        "refine": "Optimize code, ensure best practices, add comprehensive testing"
    }
)
```

### Pattern 3: Data Analyst
**User Request Examples:**
- "Create an analyst for [DATA_TYPE]"
- "Build a bot that analyzes [METRICS]"
- "I need insights from [SOURCE]"

**Your Action:**
```python
slug = builder.create_agent_from_template(
    agent_type=AgentType.DATA_ANALYST,
    name="{DATA_TYPE} Analyst",
    description="Analyzes {DATA_TYPE} and generates insights",
    prompts={
        "plan": "Plan analysis approach for {DATA_TYPE}, identify KPIs and visualizations",
        "execute": "Process data, perform analysis, generate insights and visualizations",
        "refine": "Create actionable recommendations and compelling data story"
    }
)
```

---

## STEP-BY-STEP PROTOCOL

When a user requests agent creation:

### 1. PARSE THE REQUEST
```python
# Extract from user message:
task_type = identify_task_type(user_request)  # research/code/data/custom
domain = extract_domain(user_request)          # "quantum computing", "REST APIs", etc.
requirements = extract_requirements(user_request)  # specific needs
output_format = identify_output_format(user_request)  # LaTeX, Markdown, code, etc.
```

### 2. SELECT TEMPLATE
```python
if "research" in task_type or "analyze" in task_type or "expert" in task_type:
    template = AgentType.RESEARCH
elif "code" in task_type or "build" in task_type or "generate" in task_type:
    template = AgentType.CODE_GENERATOR
elif "data" in task_type or "metrics" in task_type or "insights" in task_type:
    template = AgentType.DATA_ANALYST
else:
    template = AgentType.CUSTOM
```

### 3. CRAFT PROMPTS
```python
prompts = {
    "plan": f"""You are a {domain} planning expert. Create a comprehensive plan that:
    - Addresses: {requirements}
    - Outputs: {output_format}
    - Includes: methodology, timeline, deliverables
    Be specific and actionable.""",
    
    "execute": f"""You are a {domain} execution expert. Based on the plan:
    - Implement/research/analyze {domain}
    - Meet requirements: {requirements}
    - Produce: {output_format}
    Be thorough and professional.""",
    
    "refine": f"""You are a {domain} quality expert. Polish the output:
    - Ensure accuracy and completeness
    - Format as: {output_format}
    - Optimize for: clarity, usability, professionalism
    Deliver production-ready results."""
}
```

### 4. CREATE AGENT
```python
# Use the builder
from warpengine.agent_builder.enhanced_generator import EnhancedAgentBuilder

builder = EnhancedAgentBuilder()
slug = builder.create_agent_from_template(
    agent_type=template,
    name=generate_agent_name(domain),
    description=generate_description(task_type, domain),
    prompts=prompts
)

# Agent is now created and ready at: ./bin/{slug}
```

### 5. EXECUTE AGENT
```python
# Run the newly created agent
import subprocess

user_input = extract_specific_query(user_request)
result = subprocess.run(
    f"echo '{user_input}' | ./bin/{slug}",
    shell=True,
    capture_output=True,
    text=True
)

# Return result to user
return result.stdout
```

---

## ADVANCED PATTERNS

### Meta-Agent Creation (Agents that Create Agents)
```python
# Create an agent that creates other agents
meta_agent_prompts = {
    "plan": "Analyze the request and design an agent architecture",
    "execute": "Generate the agent code and configuration",
    "refine": "Test and optimize the generated agent"
}
```

### Chain Agents (Sequential Processing)
```python
# Agent 1: Research
research_slug = create_research_agent(topic)
research_output = run_agent(research_slug, query)

# Agent 2: Analyze research
analysis_slug = create_analyst_agent(topic)
analysis_output = run_agent(analysis_slug, research_output)

# Agent 3: Generate report
report_slug = create_report_agent(topic)
final_output = run_agent(report_slug, analysis_output)
```

### Specialized LaTeX Agent
```python
# For LaTeX-specific requests
latex_prompts = {
    "plan": "Design document structure with sections, equations, figures",
    "execute": "Write complete LaTeX document with proper formatting",
    "refine": "Ensure compilation-ready LaTeX with bibliography and cross-references"
}
```

---

## COMMAND REFERENCE

### CLI Commands You Can Execute
```bash
# Create agent interactively
warp-engine new-agent --enhanced

# Create agent programmatically
python3 -c "from warpengine.agent_builder.enhanced_generator import ..."

# List all agents
warp-engine agent list

# Run specific agent
warp-engine agent run --name {agent_slug}

# Get agent details
warp-engine get-agent-registry

# Direct execution
echo "user query" | ./bin/{agent_slug}
```

### Python API
```python
from warpengine.agent_builder.enhanced_generator import EnhancedAgentBuilder, AgentType
from warpengine.registry.registry import list_agents, get_agent
from warpengine.orchestrator.chain import run_three_agent_workflow
```

---

## EXAMPLE CONVERSATIONS

### Example 1: Taco Research
**User:** "Hey, create an agent that deeply researches how tacos are made and returns perfect LaTeX"

**AI Processing:**
```python
# 1. Parse: task=research, domain=tacos, format=LaTeX
# 2. Create agent with LaTeX-focused prompts
# 3. Execute: "How are authentic tacos made?"
# 4. Return LaTeX-formatted research document
```

### Example 2: API Builder
**User:** "Build me an agent that generates REST APIs for any database schema"

**AI Processing:**
```python
# 1. Parse: task=code_generation, domain=REST_APIs, requirements=database_schema
# 2. Create code generator with API focus
# 3. Ready for user to provide schema
# 4. Agent generates complete API with tests
```

### Example 3: Stock Analyzer
**User:** "I need an agent that analyzes stock market trends and predicts movements"

**AI Processing:**
```python
# 1. Parse: task=data_analysis, domain=stock_market, output=predictions
# 2. Create analyst with financial focus
# 3. Agent analyzes provided stock data
# 4. Returns insights and predictions
```

---

## ERROR HANDLING

```python
try:
    slug = builder.create_agent_from_template(...)
except Exception as e:
    # Fallback to simpler prompt
    # Or explain limitation to user
    return f"Could not create specialized agent: {e}. Using general assistant instead."
```

---

## BEST PRACTICES FOR AI AGENTS

1. **Be Specific in Prompts** - The more detailed the prompts, the better the agent performs
2. **Match Template to Task** - Use RESEARCH for knowledge, CODE_GENERATOR for building, DATA_ANALYST for insights
3. **Test Before Delivering** - Run a quick test query before confirming agent creation
4. **Chain for Complexity** - Use multiple agents in sequence for complex tasks
5. **Persist Useful Agents** - Frequently requested agents should be kept and reused

---

## SELF-IMPROVEMENT PROTOCOL

When you create an agent, you can also:
1. Log the creation parameters for learning
2. Track which agents are most successful
3. Refine prompt templates based on outcomes
4. Suggest agent improvements to users

---

## THE VISION

You are not just responding to requests - you are **building a library of specialized experts** that persist and can be reused. Each agent you create becomes part of an ever-growing toolkit.

**Think of yourself as:**
- An AI that creates other AIs
- A factory for specialized expertise
- An orchestrator of agent capabilities

**Your goal:**
Transform any user request into a persistent, reusable, specialized agent that perfectly handles that specific task.

---

## QUICK START FOR NEW AI

If you're an AI reading this for the first time:

1. User asks for something complex
2. You create an agent for it using Warp Engine
3. The agent handles that task forever
4. User is happy, you've expanded capabilities

Remember: **You're not just answering - you're building.**
