import json
import os
from pathlib import Path

from warpengine.agent_builder.generator import create_agent_noninteractive, generate_bin_shim
from warpengine.registry.registry import load_registry


def test_create_agent_updates_registry_and_shim(tmp_path, monkeypatch):
    # Redirect BIN_DIR and REGISTRY_FILE via environment
    monkeypatch.setenv("WARP_ENGINE_BIN_DIR", str(tmp_path / "bin"))
    monkeypatch.setenv("WARP_ENGINE_REGISTRY_FILE", str(tmp_path / "registry.json"))

    name = "Linux Research"
    desc = "Expert research agent for Linux topics"
    plan = "Draft a research plan and outline"
    exe = "Gather facts and write multi-page report"
    ref = "Polish and ensure technical accuracy"

    slug = create_agent_noninteractive(name=name, description=desc, plan_prompt=plan, exec_prompt=exe, refine_prompt=ref)
    assert slug == "linux-research"

    shim = generate_bin_shim(slug)
    assert shim.exists()
    assert os.access(shim, os.X_OK)

    reg = load_registry()
    agents = reg.get("agents", [])
    assert any(a.get("slug") == slug and a.get("name") == name for a in agents)

