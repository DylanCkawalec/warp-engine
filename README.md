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

2) Set environment variables (do NOT paste secrets into history unprotected). In zsh:
   - export WARP_ENGINE_API_KEY={{YOUR_API_KEY}}
   - export WARP_ENGINE_API_BASE=${WARP_ENGINE_API_BASE:-http://localhost:7001}

3) Run the UI server:
   - warp-engine serve --port 8787 --open-browser
   Visit http://127.0.0.1:8787/latex

4) Or run via CLI (pastes from stdin until EOF):
   - warp-engine run-latex

Warp Workflow (in Warp)
- Create a workflow named "run latex engine"
- Command:
  /Users/dylanckawalec/Desktop/developer/warp-engine/.venv/bin/warp-engine run-latex --ui

Configuration
- WARP_ENGINE_API_KEY: your bearer token (required to call your API)
- WARP_ENGINE_API_BASE: base URL for your local A2A API (default http://localhost:7001)
- WARP_ENGINE_PORT: default UI port (8787)

Notes
- The A2A client expects a POST ${WARP_ENGINE_API_BASE}/a2a/complete endpoint and returns JSON with an "output" field. Adapt client.py to your API.
- Cache is stored in data/cache.json with job records.

