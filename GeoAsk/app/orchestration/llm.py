"""The LLM boundary.

The orchestrator depends on a small ``LLMClient`` protocol, not on the Anthropic
SDK directly, so the parse→plan→execute→assemble loop can be driven by a scripted
fake in tests (no API key, deterministic) and by real Claude in production. This
mirrors how the isochrone router and the PostGIS source are injected.

``AnthropicClient`` uses Claude with adaptive thinking. Tool schemas come from
``tools.TOOL_SCHEMAS``; the model plans in terms of those validated operations.
"""

from __future__ import annotations

import os
from typing import Any, Protocol

MODEL = "claude-opus-4-8"


class LLMClient(Protocol):
    def respond(
        self, system: str, tools: list[dict[str, Any]], messages: list[dict[str, Any]]
    ) -> Any:
        """Return an object exposing ``.content`` (a list of blocks, each with a
        ``.type``; tool_use blocks also carry ``.id``/``.name``/``.input``) and
        ``.stop_reason``. The returned ``.content`` is appended verbatim to the
        message history, so it must round-trip back to the same client."""
        ...


class AnthropicClient:
    def __init__(self, model: str = MODEL, max_tokens: int = 8000):
        import anthropic

        self._client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY / profile
        self._model = model
        self._max_tokens = max_tokens

    def respond(self, system, tools, messages):
        return self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            thinking={"type": "adaptive"},
            system=system,
            tools=tools,
            messages=messages,
        )


def default_client() -> LLMClient | None:
    """A real client if credentials are configured, else ``None`` so callers can
    fall back (the orchestrator requires an explicit client in tests)."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return AnthropicClient()
    return None
