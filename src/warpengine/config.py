import os
from pathlib import Path
from typing import Optional


def project_root() -> Path:
    # src/warpengine/... => project root is 3 levels up
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = project_root()
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = PROJECT_ROOT / "input_files"
CACHE_FILE = DATA_DIR / "cache.json"


def env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


API_BASE = env("WARP_ENGINE_API_BASE", "http://localhost:7001")
API_KEY = env("WARP_ENGINE_API_KEY")  # required for authenticated calls
DEFAULT_HOST = env("WARP_ENGINE_HOST", "127.0.0.1")
DEFAULT_PORT = int(env("WARP_ENGINE_PORT", "8787"))

