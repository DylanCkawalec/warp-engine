from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests

from ..config import API_BASE, API_KEY, env

# Try to import OpenAI client
try:
    from .openai_client import OpenAIAgentClient

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class A2AClient:
    """Thin HTTP client for your local A2A API.

    Expected endpoint (adjust as needed):
      POST {API_BASE}/a2a/complete
      Body: {
        "job_id": str,
        "agent": str,
        "input": str,
        "context": dict | None,
        "mode": "high_reasoning"
      }
      Returns: { "id": str, "output": str, ... }
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_s: int = 120,
    ) -> None:
        self.base_url = (base_url or API_BASE).rstrip("/")
        self.api_key = api_key or API_KEY or env("OPENAI_API_KEY")
        self.timeout_s = timeout_s

        # Use OpenAI client if available and API key is present
        self.openai_client = None
        if OPENAI_AVAILABLE and (env("OPENAI_API_KEY") or self.api_key):
            try:
                self.openai_client = OpenAIAgentClient(api_key=self.api_key)
            except Exception:
                pass

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def complete(
        self,
        *,
        job_id: str,
        agent: str,
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "high_reasoning",
    ) -> Dict[str, Any]:
        # Use OpenAI client if available
        if self.openai_client:
            return self.openai_client.complete(
                job_id=job_id,
                agent=agent,
                input_text=input_text,
                context=context,
                mode=mode,
            )

        # Fallback to HTTP API
        url = f"{self.base_url}/a2a/complete"
        body = {
            "job_id": job_id,
            "agent": agent,
            "input": input_text,
            "context": context or {},
            "mode": mode,
        }
        try:
            resp = requests.post(
                url,
                headers=self._headers(),
                data=json.dumps(body),
                timeout=self.timeout_s,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            # Provide a helpful error and fallback dummy response so the rest of the UX still works.
            dummy = {
                "id": job_id,
                "output": f"[A2A API unavailable at {url}. Please set WARP_ENGINE_API_BASE and start your validator server, or set OPENAI_API_KEY to use OpenAI. Error: {e}]",
                "agent": agent,
                "context": context or {},
            }
            return dummy
