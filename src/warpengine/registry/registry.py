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

