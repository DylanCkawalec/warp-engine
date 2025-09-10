from __future__ import annotations

import time
from typing import Tuple

from ..api.client import A2AClient
from ..storage.cache import new_job_id, put_record
from ..metrics.analysis import analyze_text_pair


def _agent_prompt_plan(latex: str) -> str:
    return (
        "You are Agent-Plan. Read the LaTeX input and propose a concise plan (bullets) for transforming it into "
        "a finalized, readable text output. If the LaTeX contains sections, equations, or citations, include how to "
        "handle them. Output only the plan."
    )


def _agent_prompt_execute(latex: str, plan: str) -> str:
    return (
        "You are Agent-Exec. Execute the plan against the LaTeX input, producing the best possible text. "
        "Do not include the plan itself."
    )


def _agent_prompt_refine(draft: str) -> str:
    return (
        "You are Agent-Refine. Improve clarity, fix formatting artifacts, and ensure the text reads naturally. "
        "Return only the final text."
    )


def run_latex_workflow(latex: str) -> Tuple[str, str]:
    """Run a simple 3-agent chain and return (job_id, final_output)."""
    client = A2AClient()
    job_id = new_job_id()

    t0 = time.perf_counter()
    # 1) Plan
    t_plan_start = time.perf_counter()
    plan_resp = client.complete(
        job_id=job_id,
        agent="agent_plan",
        input_text=latex,
        context={"prompt": _agent_prompt_plan(latex)},
        mode="high_reasoning",
    )
    t_plan_end = time.perf_counter()
    plan_text = plan_resp.get("output", "[no plan]")

    # 2) Execute
    t_exec_start = time.perf_counter()
    exec_resp = client.complete(
        job_id=job_id,
        agent="agent_exec",
        input_text=latex,
        context={"plan": plan_text, "prompt": _agent_prompt_execute(latex, plan_text)},
        mode="high_reasoning",
    )
    t_exec_end = time.perf_counter()
    draft_text = exec_resp.get("output", "[no draft]")

    # 3) Refine
    t_refine_start = time.perf_counter()
    refine_resp = client.complete(
        job_id=job_id,
        agent="agent_refine",
        input_text=draft_text,
        context={"prompt": _agent_prompt_refine(draft_text)},
        mode="high_reasoning",
    )
    t_refine_end = time.perf_counter()
    final_text = refine_resp.get("output", "[no final]")

    t1 = time.perf_counter()

    # Compute metrics comparing input and final output
    metrics = analyze_text_pair(latex, final_text)

    # Persist record with timings and metrics
    put_record(job_id, {
        "input_kind": "latex",
        "timings": {
            "plan_s": t_plan_end - t_plan_start,
            "exec_s": t_exec_end - t_exec_start,
            "refine_s": t_refine_end - t_refine_start,
            "total_s": t1 - t0,
        },
        "lengths": {
            "latex_chars": len(latex),
            "plan_chars": len(plan_text),
            "draft_chars": len(draft_text),
            "final_chars": len(final_text),
        },
        "plan": plan_text,
        "draft": draft_text,
        "final": final_text,
        "metrics": metrics,
    })
    return job_id, final_text


def run_latex_workflow_cli(latex: str) -> Tuple[str, str]:
    return run_latex_workflow(latex)

