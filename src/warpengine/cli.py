import argparse
import sys
import webbrowser
from typing import Optional

from .server.ui import run_server
from .orchestrator.chain import run_latex_workflow_cli


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


if __name__ == "__main__":
    main()

