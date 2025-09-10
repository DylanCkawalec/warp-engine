from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import CACHE_FILE, DATA_DIR


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def new_job_id() -> str:
    return str(uuid.uuid4())


def read_cache() -> Dict[str, Any]:
    ensure_dirs()
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_cache(cache: Dict[str, Any]) -> None:
    ensure_dirs()
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def put_record(job_id: str, record: Dict[str, Any]) -> None:
    cache = read_cache()
    cache[job_id] = record
    write_cache(cache)


def get_record(job_id: str) -> Optional[Dict[str, Any]]:
    return read_cache().get(job_id)
