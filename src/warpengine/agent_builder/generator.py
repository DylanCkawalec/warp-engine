from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from ..config import AGENTS_ROOT, BIN_DIR
from ..registry.registry import upsert_agent


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or "agent"


def ensure_dirs() -> None:
    AGENTS_ROOT.mkdir(parents=True, exist_ok=True)
    BIN_DIR.mkdir(parents=True, exist_ok=True)


def create_agent_noninteractive(*, name: str, description: str, plan_prompt: str, exec_prompt: str, refine_prompt: str) -> str:
    slug = slugify(name)
    ensure_dirs()

    pkg_dir = AGENTS_ROOT / slug
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # __init__.py
    (pkg_dir / "__init__.py").write_text("\n", encoding="utf-8")

    # runner.py uses orchestrator.chain.run_three_agent_workflow
    runner_py = f"""
from __future__ import annotations
from typing import Tuple

from warpengine.orchestrator.chain import run_three_agent_workflow

PROMPTS = {{
    "plan": {plan_prompt!r},
    "execute": {exec_prompt!r},
    "refine": {refine_prompt!r},
}}


def run(text: str) -> Tuple[str, str]:
    return run_three_agent_workflow(text, PROMPTS)
"""
    (pkg_dir / "runner.py").write_text(runner_py, encoding="utf-8")

    # Update registry entry
    upsert_agent({
        "name": name,
        "slug": slug,
        "description": description,
        "entry": f"warpengine.agents.{slug}.runner:run",
        "prompts": {
            "plan": plan_prompt,
            "execute": exec_prompt,
            "refine": refine_prompt,
        },
        "type": "workflow",
    })

    return slug


def create_agent_interactive() -> str:
    name = input("Agent name: ").strip()
    description = input("Description: ").strip()
    print("\nProvide three prompts for the agent (Plan / Execute / Refine). Leave blank to use defaults.\n")
    plan_prompt = input("Plan prompt: ").strip() or "You are Agent-Plan. Produce a concise plan."
    exec_prompt = input("Execute prompt: ").strip() or "You are Agent-Exec. Execute the plan against the input."
    refine_prompt = input("Refine prompt: ").strip() or "You are Agent-Refine. Improve clarity and correctness."
    return create_agent_noninteractive(
        name=name,
        description=description,
        plan_prompt=plan_prompt,
        exec_prompt=exec_prompt,
        refine_prompt=refine_prompt,
    )


def generate_bin_shim(slug: str) -> Path:
    ensure_dirs()
    shim = BIN_DIR / slug
    content = f"""#!/usr/bin/env python3
import sys
from importlib import import_module

mod = import_module("warpengine.agents.{slug}.runner")
print("Paste input text, then Ctrl-D (EOF):\n", file=sys.stderr)
text = sys.stdin.read()
job_id, final = mod.run(text)
print(final)
print(f"\n[job_id={{job_id}}]", file=sys.stderr)
"""
    shim.write_text(content, encoding="utf-8")
    try:
        os.chmod(shim, 0o755)
    except Exception:
        pass
    return shim

