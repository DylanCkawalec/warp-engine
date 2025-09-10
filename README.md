# Warp Engine

A local A2A workflow orchestrator with a simple web UI for pasting LaTeX or uploading files. It chains three agents via your own API and returns a final text output. Runs well from Warp as a custom workflow.

Features
- Paste LaTeX or upload files via local UI (FastAPI)
- Minimal 3-agent chain (plan → execute → refine)
- Calls your local A2A API using environment variables
- Caches responses by job ID
- CLI for serving the UI or running directly from the terminal

Quick start
1) Create a venv and install:
   - python3 -m venv .venv
   - . .venv/bin/activate
   - pip install -U pip setuptools wheel
   - pip install -e .

2) Configure environment (safer via .env file):
   - cp .env.example .env
   - edit .env and set WARP_ENGINE_API_KEY and WARP_ENGINE_API_BASE
   Or, export in your shell:
   - export WARP_ENGINE_API_KEY={{YOUR_API_KEY}}
   - export WARP_ENGINE_API_BASE=${WARP_ENGINE_API_BASE:-http://localhost:7001}

3) Run the UI server:
   - warp-engine serve --port 8787 --open-browser
   Visit http://127.0.0.1:8787/latex

4) Or run via CLI (pastes from stdin until EOF):
   - warp-engine run-latex

5) Analyze a completed job's metrics:
   - warp-engine analyze --job-id <JOB_ID>
   Or via API: GET /api/jobs/<JOB_ID>/metrics

6) Agent registry and builder:
   - List agents: warp-engine agent list or GET /api/agents
   - Create new agent (interactive): warp-engine new-agent
     • Or via API: POST /api/agents { name, description, prompts: { plan, execute, refine } }
   - Run agent: warp-engine agent run --name <agent-slug>
   - Generated shim: bin/<agent-slug>

Warp Workflow (in Warp)
- Create workflows, for example:
  - "run latex engine":
    /Users/dylanckawalec/Desktop/developer/warp-engine/.venv/bin/warp-engine run-latex --ui
  - "new agent":
    /Users/dylanckawalec/Desktop/developer/warp-engine/.venv/bin/warp-engine new-agent
  - "list agents":
    /Users/dylanckawalec/Desktop/developer/warp-engine/.venv/bin/warp-engine agent list

Configuration
- WARP_ENGINE_API_KEY: your bearer token (required to call your API)
- WARP_ENGINE_API_BASE: base URL for your local A2A API (default http://localhost:7001)
- WARP_ENGINE_PORT: default UI port (8787)
- WARP_ENGINE_REGISTRY_FILE: override path to the agent registry JSON (default data/registry.json)
- WARP_ENGINE_AGENTS_ROOT: override path where new agents will be created (default src/warpengine/agents)
- WARP_ENGINE_BIN_DIR: override path where runnable shims are created (default bin)

Notes
- The A2A client expects a POST ${WARP_ENGINE_API_BASE}/a2a/complete endpoint and returns JSON with an "output" field. Adapt client.py to your API.
- Cache is stored in data/cache.json with job records. Each job includes timings per agent and metrics over input/output text.
- The universal agent registry lives at data/registry.json and is also served at GET /api/agents.

