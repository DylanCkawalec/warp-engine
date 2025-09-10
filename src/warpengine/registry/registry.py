from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..config import REGISTRY_FILE, DATA_DIR


def _ensure_parent() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_registry() -> Dict[str, Any]:
    _ensure_parent()
    if not REGISTRY_FILE.exists():
        return {"version": 1, "agents": []}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "agents": []}


def save_registry(reg: Dict[str, Any]) -> None:
    _ensure_parent()
    REGISTRY_FILE.write_text(json.dumps(reg, indent=2), encoding="utf-8")


def list_agents() -> List[Dict[str, Any]]:
    return load_registry().get("agents", [])


def get_agent(slug: str) -> Optional[Dict[str, Any]]:
    slug_norm = slug.strip().lower()
    for a in list_agents():
        if a.get("slug") == slug_norm:
            return a
    return None


def upsert_agent(agent: Dict[str, Any]) -> None:
    reg = load_registry()
    agents = reg.setdefault("agents", [])
    slug = agent.get("slug")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    agent.setdefault("updated_at", now)
    found = False
    for i, a in enumerate(agents):
        if a.get("slug") == slug:
            agent.setdefault("created_at", a.get("created_at", now))
            agents[i] = agent
            found = True
            break
    if not found:
        agent.setdefault("created_at", now)
        agents.append(agent)
    save_registry(reg)


def delete_agent(slug: str) -> bool:
    """Delete an agent from the registry and clean up its files.

    Args:
        slug: Agent slug to delete

    Returns:
        True if agent was deleted, False if not found
    """
    reg = load_registry()
    agents = reg.get("agents", [])
    slug_norm = slug.strip().lower()

    # Find and remove agent from registry
    agent_to_delete = None
    for i, agent in enumerate(agents):
        if agent.get("slug") == slug_norm:
            agent_to_delete = agent
            agents.pop(i)
            break

    if not agent_to_delete:
        return False

    # Save updated registry
    save_registry(reg)

    # Clean up agent files
    _cleanup_agent_files(slug_norm)

    return True


def _cleanup_agent_files(slug: str) -> None:
    """Clean up all files associated with an agent.

    Args:
        slug: Agent slug
    """
    from ..config import AGENTS_ROOT, BIN_DIR, DATA_DIR
    import shutil

    # Remove agent source directory
    agent_dir = AGENTS_ROOT / slug
    if agent_dir.exists():
        shutil.rmtree(agent_dir)

    # Remove agent binary
    agent_bin = BIN_DIR / slug
    if agent_bin.exists():
        agent_bin.unlink()

    # Remove agent job history
    jobs_dir = DATA_DIR / "jobs"
    if jobs_dir.exists():
        for job_file in jobs_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    job_data = json.load(f)
                # Remove jobs related to this agent
                if job_data.get("command") in ["create_agent", "run_agent"] and \
                   job_data.get("params", {}).get("agent") == slug:
                    job_file.unlink()
            except:
                pass
