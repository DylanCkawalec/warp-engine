import os
from pathlib import Path
from typing import Optional

# Load variables from .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def project_root() -> Path:
    # src/warpengine/... => project root is 3 levels up
    return Path(__file__).resolve().parents[3]


def env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(key, default)


PROJECT_ROOT = project_root()
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = PROJECT_ROOT / "input_files"
CACHE_FILE = DATA_DIR / "cache.json"

# Agent registry and builder locations (overridable via env)
AGENTS_ROOT = Path(env("WARP_ENGINE_AGENTS_ROOT", str(PROJECT_ROOT / "src" / "warpengine" / "agents")))
REGISTRY_FILE = Path(env("WARP_ENGINE_REGISTRY_FILE", str(DATA_DIR / "registry.json")))
BIN_DIR = Path(env("WARP_ENGINE_BIN_DIR", str(PROJECT_ROOT / "bin")))

API_BASE = env("WARP_ENGINE_API_BASE", "http://localhost:7001")
API_KEY = env("WARP_ENGINE_API_KEY")  # required for authenticated calls
DEFAULT_HOST = env("WARP_ENGINE_HOST", "127.0.0.1")
DEFAULT_PORT = int(env("WARP_ENGINE_PORT", "8787"))

