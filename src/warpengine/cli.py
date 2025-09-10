import argparse
import sys
import webbrowser
from typing import Optional

from .server.ui import run_server
from .orchestrator.chain import run_latex_workflow_cli
from .registry.registry import list_agents, get_agent, load_registry
from .agent_builder.generator import create_agent_interactive, create_agent_noninteractive, generate_bin_shim


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(prog="warp-engine", description="Local A2A workflow orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="Start the local UI server")
    p_serve.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    p_serve.add_argument("--port", type=int, default=8787, help="Port to bind (default: 8787)")
    p_serve.add_argument("--open-browser", action="store_true", help="Open browser to the LaTeX page")

    p_run = sub.add_parser("run-latex", help="Run LaTeX workflow (UI or CLI mode)")
    p_run.add_argument("--ui", action="store_true", help="Open the browser UI for LaTeX input")
    p_run.add_argument("--host", default="127.0.0.1", help="UI host when using --ui (default: 127.0.0.1)")
    p_run.add_argument("--port", type=int, default=8787, help="UI port when using --ui (default: 8787)")

    p_analyze = sub.add_parser("analyze", help="Analyze a completed job and print metrics")
    p_analyze.add_argument("--job-id", help="Existing job id to analyze (required)")

    p_reg = sub.add_parser("get-agent-registry", help="Print the agent registry as JSON")

    p_new = sub.add_parser("new-agent", help="Create a new agent via prompts or flags")
    p_new.add_argument("--name", help="Agent name")
    p_new.add_argument("--description", help="Agent description")
    p_new.add_argument("--plan-prompt", help="Plan prompt text")
    p_new.add_argument("--exec-prompt", help="Execute prompt text")
    p_new.add_argument("--refine-prompt", help="Refine prompt text")

    p_agent = sub.add_parser("agent", help="Work with agents")
    sp = p_agent.add_subparsers(dest="agent_cmd", required=True)
    p_list = sp.add_parser("list", help="List registered agents")
    p_run_agent = sp.add_parser("run", help="Run an agent workflow with pasted input from stdin")
    p_run_agent.add_argument("--name", required=True, help="Agent name to run")

    args = parser.parse_args(argv)

    if args.cmd == "serve":
        run_server(host=args.host, port=args.port)
        if args.open_browser:
            webbrowser.open_new_tab(f"http://{args.host}:{args.port}/latex")
        return

    if args.cmd == "run-latex":
        if args.ui:
            # Start (or assume) server and open page. For simplicity, just open the page.
            # If the server is not yet running, the user can start it via `warp-engine serve --open-browser`.
            webbrowser.open_new_tab(f"http://{args.host}:{args.port}/latex")
            print("Opened LaTeX UI in your browser. If you don't see it, run: `warp-engine serve --open-browser`.")
            return
        # CLI mode: read stdin for LaTeX until EOF (Ctrl-D)
        print("Paste LaTeX, then press Ctrl-D (EOF) to submit:\n", file=sys.stderr)
        latex = sys.stdin.read()
        if not latex.strip():
            print("No LaTeX provided.", file=sys.stderr)
            sys.exit(1)
        job_id, final_output = run_latex_workflow_cli(latex)
        print(final_output)
        print(f"\n[job_id={job_id}]", file=sys.stderr)
        return

    if args.cmd == "analyze":
        if not args.job_id:
            print("--job-id is required", file=sys.stderr)
            sys.exit(2)
        from .storage.cache import get_record
        from .metrics.analysis import extract_printable_metrics
        rec = get_record(args.job_id)
        if not rec:
            print("Job not found", file=sys.stderr)
            sys.exit(3)
        metrics = rec.get("metrics") or {}
        print(extract_printable_metrics(metrics))
        return

    if args.cmd == "get-agent-registry":
        reg = load_registry()
        import json
        print(json.dumps(reg, indent=2))
        return

    if args.cmd == "new-agent":
        if args.name and args.description and args.plan_prompt and args.exec_prompt and args.refine_prompt:
            slug = create_agent_noninteractive(
                name=args.name,
                description=args.description,
                plan_prompt=args.plan_prompt,
                exec_prompt=args.exec_prompt,
                refine_prompt=args.refine_prompt,
            )
        else:
            slug = create_agent_interactive()
        # Create a runnable shim in bin/
        shim_path = generate_bin_shim(slug)
        print(f"Created agent '{slug}'. Run it with: {shim_path} or via 'warp-engine agent run --name {slug}'")
        return

    if args.cmd == "agent":
        if args.agent_cmd == "list":
            agents = list_agents()
            for a in agents:
                print(f"- {a['name']} ({a['slug']}) : {a.get('description','')}")
            return
        if args.agent_cmd == "run":
            agent = get_agent(args.name)
            if not agent:
                print("Agent not found", file=sys.stderr)
                sys.exit(4)
            # Import the runner dynamically
            import importlib
            module_path, func_name = agent["entry"].split(":")
            mod = importlib.import_module(module_path)
            run_fn = getattr(mod, func_name)
            print("Paste input text, then Ctrl-D (EOF):\n", file=sys.stderr)
            text = sys.stdin.read()
            job_id, final_output = run_fn(text)
            print(final_output)
            print(f"\n[job_id={job_id}]", file=sys.stderr)
            return


if __name__ == "__main__":
    main()

