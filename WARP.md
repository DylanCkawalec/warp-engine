# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project overview
- Python 3.10+ package providing a local agent workflow engine with:
  - CLI entrypoint (warp-engine)
  - Three-agent orchestrator (plan → execute → refine)
  - FastAPI server for a simple UI and REST API
  - Agent registry and code generation (basic and enhanced templates)
  - Optional Warp Terminal integrations (profiles/workflows) if the Warp CLI is available

Commands (day-to-day)
- Environment and install
  - python3 -m venv .venv
  - source .venv/bin/activate
  - python -m pip install -U pip
  - pip install -e .[test]
- Run the local UI server
  - warp-engine serve --open-browser
  - OpenUI: http://127.0.0.1:8787
- Run the LaTeX workflow
  - Browser UI: warp-engine run-latex --ui
  - CLI via stdin: printf "\\section{Intro} Hello." | warp-engine run-latex
- Inspect results and metrics
  - warp-engine analyze --job-id <JOB_ID>
  - curl http://127.0.0.1:8787/api/jobs/<JOB_ID>
  - curl http://127.0.0.1:8787/api/jobs/<JOB_ID>/metrics
- Agent registry and execution
  - List: warp-engine agent list
  - Run (reads stdin): printf "your text" | warp-engine agent run --name <agent-slug>
  - Create (interactive templates): warp-engine new-agent --enhanced
  - Create (non-interactive):
    - warp-engine new-agent \
      --name "Linux Research" \
      --description "Expert research" \
      --plan-prompt "Plan..." \
      --exec-prompt "Execute..." \
      --refine-prompt "Refine..."
  - After creation, a runnable shim is written to bin/<agent-slug>
- Tests
  - Run all: pytest -q
  - Verbose in tests/: pytest tests/ -v
  - Single test: pytest tests/test_orchestrator.py::test_chain_with_dummy_client -q
  - By keyword: pytest -k refine -q
- Lint/format
  - No linter/formatter is configured in pyproject.toml
- Optional packaging (sdist/wheel)
  - python -m pip install build
  - python -m build

Key environment variables
- OPENAI_API_KEY: Enables direct OpenAI execution via the OpenAI Chat Completions API. If set (and openai is installed), the orchestrator uses the OpenAI client instead of the HTTP A2A endpoint.
- WARP_ENGINE_API_BASE: Base URL for the fallback HTTP A2A API (default: http://localhost:7001)
- WARP_ENGINE_HOST / WARP_ENGINE_PORT: FastAPI server host/port (defaults: 127.0.0.1 / 8787)
- WARP_ENGINE_AGENTS_ROOT: Where generated agents are created (default: src/warpengine/agents)
- WARP_ENGINE_REGISTRY_FILE: Agent registry JSON path (default: data/registry.json)
- WARP_ENGINE_BIN_DIR: Output directory for agent shims (default: bin/)

High-level architecture (big picture)
- CLI (src/warpengine/cli.py)
  - Subcommands:
    - serve: starts the FastAPI app (run_server)
    - run-latex: runs the LaTeX flow via UI (browser) or via stdin (CLI)
    - analyze: pretty-prints metrics for a completed job from the cache
    - get-agent-registry: prints the agent registry JSON
    - new-agent: creates agents (basic or enhanced builder); also writes bin/ shims
    - agent list/run: lists agents from the registry; dynamically imports and runs the selected agent’s runner
  - Note: agent run loads entry from registry and importlib loads the runner function specified by entry
- Orchestrator (src/warpengine/orchestrator/chain.py)
  - Core primitive run_three_agent_workflow(input_text, prompts):
    - Plan → Execute → Refine sequence, each step calling A2AClient.complete(...)
    - Records timings, text lengths, and metrics (see metrics) into the cache with a generated job_id
  - Convenience wrappers for LaTeX (run_latex_workflow, run_latex_workflow_cli)
- API and model selection (src/warpengine/api)
  - client.A2AClient: Tries to use OpenAIAgentClient if openai and OPENAI_API_KEY are available; otherwise posts to {WARP_ENGINE_API_BASE}/a2a/complete
  - openai_client.OpenAIAgentClient: Builds system/user messages from prompts/context and calls the OpenAI Chat Completions API; model selection varies by mode (e.g., high_reasoning)
- Server (src/warpengine/server/ui.py)
  - FastAPI app with:
    - / (index) and /latex (simple HTML form)
    - /api/run-latex: runs the workflow, returns {id, final}
    - /api/jobs/{id}, /api/jobs/{id}/metrics: inspect cached job records and recomputed metrics
    - /api/agents (GET/POST), /api/agents/{slug}: list, create, and fetch agents via registry + builder
- Storage and registry
  - storage/cache.py: data/cache.json stores job records keyed by job_id (timings, lengths, prompts, final output, metrics)
  - registry/registry.py: data/registry.json persists agents with (name, slug, description, entry, prompts, timestamps)
- Agent builders (src/warpengine/agent_builder)
  - generator.py: basic noninteractive/interactive agent creation; writes a minimal runner using run_three_agent_workflow and updates the registry; generates bin/<slug> shim that reads stdin and prints output
  - enhanced_generator.py: template-driven (research/code_generator/data_analyst/custom); creates runner, test file for the agent, requirements.txt, registry entry, and bin shim; optionally creates Warp profiles/workflows if the Warp CLI is available; runs pytest on the generated test to validate
- Warp integration (src/warpengine/warp_integration)
  - warp_client.py provides a best-effort abstraction over the Warp CLI (if found) to create agent profiles and workflows under ~/.warp. If the CLI is not present, integration is skipped without breaking local functionality
- Configuration (src/warpengine/config.py)
  - Loads .env if present; centralizes project dirs (PROJECT_ROOT, DATA_DIR, BIN_DIR, AGENTS_ROOT) and defaults for API and server

REST API quick reference
- POST /api/run-latex → { id, final }
- GET  /api/jobs/{id} → job record (timings, texts, metrics)
- GET  /api/jobs/{id}/metrics → metrics only
- GET  /api/agents → { agents: [...] }
- POST /api/agents → { slug, shim } (expects name, description, prompts.{plan,execute,refine})
- GET  /api/agents/{slug} → agent details

Testing strategy (what’s covered)
- tests/test_metrics.py: tokenization, syllable counts, readability, n-grams
- tests/test_orchestrator.py: deterministic 3-step chain via a dummy client (monkeypatched A2AClient)
- tests/test_server.py: FastAPI endpoint /api/run-latex using TestClient
- tests/test_registry.py: agent creation updates registry and writes executable shim

Notes from README.md
- The README documents CLI usage (new-agent, agent list/run, serve) and the three-agent lifecycle; those flows match the current code
- Some directories and advanced features in the README (e.g., pre-populated data/ and config.api.json) are optional or created at runtime if missing; code paths handle absence gracefully

