"""OpenAI client for agent-to-agent communication."""

from __future__ import annotations

import json
import os
import time
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import openai
from openai import OpenAI

from ..config import env


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 50):
        """Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.call_times: List[datetime] = []

    def can_make_call(self) -> bool:
        """Check if a call can be made without exceeding rate limit."""
        now = datetime.now()

        # Remove calls older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self.call_times = [t for t in self.call_times if t > cutoff]

        return len(self.call_times) < self.calls_per_minute

    def record_call(self) -> None:
        """Record a call for rate limiting."""
        self.call_times.append(datetime.now())

    async def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        while not self.can_make_call():
            await asyncio.sleep(1)

        self.record_call()


@dataclass
class AgentResponse:
    """Response from an agent."""

    id: str
    output: str
    agent: str
    context: Dict[str, Any]
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    duration_ms: Optional[int] = None


class OpenAIAgentClient:
    """OpenAI-powered agent client for the Universal Agent Protocol."""

    def __init__(
        self, api_key: Optional[str] = None, config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            config: Configuration dict from config.api.json
        """
        self.api_key = api_key or env("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key)

        # Load config from config.api.json if provided
        self.config = config or {}
        self.api_config = self.config.get("api", {}).get("openai", {})

        # Model preferences
        self.model_preferences = self.api_config.get(
            "model_preferences", ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
        )
        self.default_model = self.model_preferences[0]

        # Parameters
        self.max_tokens = self.api_config.get("max_tokens", 4096)
        self.temperature = self.api_config.get("temperature", 0.7)

        # Rate limiter (50 calls per minute by default)
        self.rate_limiter = RateLimiter(calls_per_minute=50)

        # Usage tracking
        self.usage_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "calls_this_minute": 0,
            "last_minute_reset": time.time()
        }

    def _select_model(self, mode: str) -> str:
        """Select the appropriate model based on mode.

        Args:
            mode: The reasoning mode (high_reasoning, fast, balanced)

        Returns:
            Model name
        """
        if mode == "high_reasoning":
            # Use the most capable model for complex reasoning
            return (
                self.model_preferences[0]
                if self.model_preferences
                else "gpt-4-turbo-preview"
            )
        elif mode == "fast":
            # Use a faster model for quick responses
            return "gpt-3.5-turbo"
        else:
            # Balanced mode - use second preference or default
            return (
                self.model_preferences[1]
                if len(self.model_preferences) > 1
                else self.default_model
            )

    def _build_messages(
        self, agent: str, input_text: str, context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Build the message array for OpenAI API.

        Args:
            agent: Agent identifier
            input_text: Input text to process
            context: Additional context including prompts

        Returns:
            List of message dicts
        """
        messages = []

        # System message from context prompt
        system_prompt = context.get("prompt", "")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add plan if provided (for execute agent)
        if "plan" in context and context["plan"]:
            messages.append(
                {
                    "role": "system",
                    "content": f"Previous agent's plan:\n{context['plan']}",
                }
            )

        # User message with input
        messages.append({"role": "user", "content": input_text})

        return messages

    def complete(
        self,
        job_id: str,
        agent: str,
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "high_reasoning",
    ) -> Dict[str, Any]:
        """Execute an agent completion using OpenAI.

        Args:
            job_id: Unique job identifier
            agent: Agent name (e.g., "agent_plan", "agent_exec", "agent_refine")
            input_text: Input text to process
            context: Additional context including prompts
            mode: Reasoning mode (high_reasoning, fast, balanced)

        Returns:
            Agent response dict
        """
        context = context or {}
        start_time = time.time()

        # Apply rate limiting (synchronous version)
        if not self.rate_limiter.can_make_call():
            return {
                "id": job_id,
                "output": "[Rate Limited: Too many API calls per minute]",
                "agent": agent,
                "context": context,
                "rate_limited": True,
            }
        self.rate_limiter.record_call()

        try:
            # Select model based on mode
            model = self._select_model(mode)

            # Build messages
            messages = self._build_messages(agent, input_text, context)

            # Make API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1,
            )

            # Extract response
            output = response.choices[0].message.content
            usage = (
                {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else None
            )

            # Update usage statistics
            self._update_usage_stats(usage)

            duration_ms = int((time.time() - start_time) * 1000)

            return {
                "id": job_id,
                "output": output,
                "agent": agent,
                "context": context,
                "usage": usage,
                "model": model,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            # Return error response
            return {
                "id": job_id,
                "output": f"[OpenAI API Error: {str(e)}]",
                "agent": agent,
                "context": context,
                "error": str(e),
            }

    def _update_usage_stats(self, usage: Optional[Dict[str, int]]) -> None:
        """Update usage statistics."""
        if usage:
            self.usage_stats["total_calls"] += 1
            self.usage_stats["total_tokens"] += usage.get("total_tokens", 0)

            # Rough cost estimation ($0.002 per 1K tokens for GPT-4)
            tokens = usage.get("total_tokens", 0)
            cost = (tokens / 1000) * 0.002
            self.usage_stats["total_cost"] += cost

        # Update per-minute stats
        now = time.time()
        if now - self.usage_stats["last_minute_reset"] >= 60:
            self.usage_stats["calls_this_minute"] = 0
            self.usage_stats["last_minute_reset"] = now

        self.usage_stats["calls_this_minute"] += 1

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return {
            "total_calls": self.usage_stats["total_calls"],
            "total_tokens": self.usage_stats["total_tokens"],
            "total_cost": round(self.usage_stats["total_cost"], 4),
            "calls_this_minute": self.usage_stats["calls_this_minute"],
            "rate_limited": not self.rate_limiter.can_make_call()
        }

    def complete_batch(self, completions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple agent completions.

        Args:
            completions: List of completion requests

        Returns:
            List of agent responses
        """
        results = []
        for completion in completions:
            result = self.complete(**completion)
            results.append(result)
        return results

    def stream_complete(
        self,
        job_id: str,
        agent: str,
        input_text: str,
        context: Optional[Dict[str, Any]] = None,
        mode: str = "high_reasoning",
        callback: Optional[callable] = None,
    ):
        """Stream an agent completion using OpenAI.

        Args:
            job_id: Unique job identifier
            agent: Agent name
            input_text: Input text to process
            context: Additional context
            mode: Reasoning mode
            callback: Optional callback for streaming chunks

        Yields:
            Streaming response chunks
        """
        context = context or {}

        try:
            model = self._select_model(mode)
            messages = self._build_messages(agent, input_text, context)

            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    if callback:
                        callback(content)
                    yield content

        except Exception as e:
            yield f"[OpenAI Streaming Error: {str(e)}]"


# Backward compatibility with existing A2AClient
class A2AClient(OpenAIAgentClient):
    """Backward-compatible wrapper for OpenAI client."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_s: int = 120,
    ):
        """Initialize with backward compatibility.

        Args:
            base_url: Ignored (for backward compatibility)
            api_key: OpenAI API key
            timeout_s: Timeout in seconds (used for client configuration)
        """
        super().__init__(api_key=api_key)
        self.timeout_s = timeout_s
