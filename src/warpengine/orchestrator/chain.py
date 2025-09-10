from __future__ import annotations

import time
from typing import Dict, Tuple, Optional

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


def run_three_agent_workflow(
    input_text: str,
    prompts: Dict[str, str],
    *,
    input_kind: str = "text",
    client: Optional[A2AClient] = None,
) -> Tuple[str, str]:
    """Generic 3-agent chain with plan/execute/refine prompts."""
    client = client or A2AClient()
    job_id = new_job_id()

    t0 = time.perf_counter()
    # 1) Plan
    t_plan_start = time.perf_counter()
    plan_resp = client.complete(
        job_id=job_id,
        agent="agent_plan",
        input_text=input_text,
        context={"prompt": prompts.get("plan", "")},
        mode="high_reasoning",
    )
    t_plan_end = time.perf_counter()
    plan_text = plan_resp.get("output", "[no plan]")

    # 2) Execute
    t_exec_start = time.perf_counter()
    exec_resp = client.complete(
        job_id=job_id,
        agent="agent_exec",
        input_text=input_text,
        context={"plan": plan_text, "prompt": prompts.get("execute", "")},
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
        context={"prompt": prompts.get("refine", "")},
        mode="high_reasoning",
    )
    t_refine_end = time.perf_counter()
    final_text = refine_resp.get("output", "[no final]")

    t1 = time.perf_counter()

    # Compute metrics comparing input and final output
    metrics = analyze_text_pair(input_text, final_text)

    # Persist record with timings and metrics
    put_record(
        job_id,
        {
            "input_kind": input_kind,
            "timings": {
                "plan_s": t_plan_end - t_plan_start,
                "exec_s": t_exec_end - t_exec_start,
                "refine_s": t_refine_end - t_refine_start,
                "total_s": t1 - t0,
            },
            "lengths": {
                "input_chars": len(input_text),
                "plan_chars": len(plan_text),
                "draft_chars": len(draft_text),
                "final_chars": len(final_text),
            },
            "plan": plan_text,
            "draft": draft_text,
            "final": final_text,
            "metrics": metrics,
        },
    )
    return job_id, final_text


def run_latex_workflow(latex: str) -> Tuple[str, str]:
    prompts = {
        "plan": _agent_prompt_plan(latex),
        "execute": _agent_prompt_execute(latex, ""),
        "refine": _agent_prompt_refine(""),
    }
    return run_three_agent_workflow(latex, prompts, input_kind="latex")


def run_latex_workflow_cli(latex: str) -> Tuple[str, str]:
    return run_latex_workflow(latex)
