from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..api.client import A2AClient
from ..storage.cache import new_job_id, put_record


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

    # 1) Plan
    plan_resp = client.complete(
        job_id=job_id,
        agent="agent_plan",
        input_text=latex,
        context={"prompt": _agent_prompt_plan(latex)},
        mode="high_reasoning",
    )
    plan_text = plan_resp.get("output", "[no plan]")

    # 2) Execute
    exec_resp = client.complete(
        job_id=job_id,
        agent="agent_exec",
        input_text=latex,
        context={"plan": plan_text, "prompt": _agent_prompt_execute(latex, plan_text)},
        mode="high_reasoning",
    )
    draft_text = exec_resp.get("output", "[no draft]")

    # 3) Refine
    refine_resp = client.complete(
        job_id=job_id,
        agent="agent_refine",
        input_text=draft_text,
        context={"prompt": _agent_prompt_refine(draft_text)},
        mode="high_reasoning",
    )
    final_text = refine_resp.get("output", "[no final]")

    # Persist record
    put_record(job_id, {
        "input_kind": "latex",
        "plan": plan_text,
        "draft": draft_text,
        "final": final_text,
    })
    return job_id, final_text


def run_latex_workflow_cli(latex: str) -> Tuple[str, str]:
    return run_latex_workflow(latex)

