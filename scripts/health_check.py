#!/usr/bin/env python3
"""
Health check script for Warp Engine production deployment.
"""

import sys
import json
import requests
from pathlib import Path


def check_service_health(base_url="http://127.0.0.1:8788"):
    """Check service health."""
    try:
        # Check root endpoint
        resp = requests.get(f"{base_url}/", timeout=5)
        if resp.status_code != 200:
            return False, f"Root endpoint failed: {resp.status_code}"

        # Check status endpoint
        resp = requests.get(f"{base_url}/api/status", timeout=5)
        if resp.status_code != 200:
            return False, f"Status endpoint failed: {resp.status_code}"

        status = resp.json()
        if not isinstance(status, dict):
            return False, "Status response not a dict"

        if not status.get("success", False):
            return False, f"Service status failed: {status}"

        return True, "Service healthy"

    except requests.RequestException as e:
        return False, f"HTTP error: {e}"
    except ValueError as e:
        return False, f"JSON parse error: {e}"
    except Exception as e:
        return False, f"Connection failed: {e}"


def check_files():
    """Check critical files exist."""
    critical_files = [
        "src/warpengine/server/engine_service.py",
        "src/warpengine/client/engine_client.py",
        "warp-engine-service",
        "warp-engine-client",
        "pyproject.toml",
        "WARP.HELP.md",
    ]

    missing = []
    for file in critical_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        return False, f"Missing files: {missing}"

    return True, "All files present"


def check_agents():
    """Check agents are available."""
    try:
        from warpengine.client.engine_client import WarpEngineClient

        client = WarpEngineClient()

        if not client.is_running():
            return False, "Service not running"

        agents = client.list_agents()
        if len(agents) < 1:
            return False, "No agents registered"

        return True, f"{len(agents)} agents available"

    except Exception as e:
        return False, f"Agent check failed: {e}"


def main():
    """Run all health checks."""
    print("🔍 Warp Engine Health Check")
    print("=" * 40)

    checks = [
        ("Files", check_files),
        ("Service", lambda: check_service_health()),
        ("Agents", check_agents),
    ]

    all_passed = True

    for name, check_func in checks:
        print(f"\n{name}: ", end="")
        try:
            success, message = check_func()
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
                all_passed = False
        except Exception as e:
            print(f"❌ Error: {e}")
            all_passed = False

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Warp Engine is healthy.")
        return 0
    else:
        print("⚠️  Some checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
