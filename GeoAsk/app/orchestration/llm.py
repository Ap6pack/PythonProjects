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

# USD per 1M tokens (input, output). Kept here so cost tracking has one source of
# truth; update when pricing changes. The plan calls out LLM cost as a risk to
# track per query from Phase 2 on.
PRICING = {
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Rough USD cost for a query's token usage (excludes cache discounts)."""
    in_rate, out_rate = PRICING.get(model, PRICING[MODEL])
    return input_tokens / 1e6 * in_rate + output_tokens / 1e6 * out_rate


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
        self.model = model  # public, for cost attribution
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


class ScriptedClient:
    """A deterministic ``LLMClient`` that replays a fixed plan of tool calls.

    Not an LLM — it plays a pre-written list of turns (each a list of
    ``(tool_name, args)``). Used to demo and test the orchestration loop with no
    API key: the loop, guardrails, layer store, and trace are exercised for real;
    only the *planning* is canned. Because layer handles are deterministic
    (layer_1, layer_2, …), a plan can reference the handles earlier steps produce.
    """

    def __init__(self, turns: list[list[tuple[str, dict[str, Any]]]]):
        from types import SimpleNamespace

        self._turns = turns
        self._i = 0
        self._ns = SimpleNamespace

    def respond(self, system, tools, messages):
        # A fresh conversation (only the user turn present) replays from the top,
        # so one instance can drive many independent questions.
        if len(messages) == 1:
            self._i = 0
        turn = self._turns[self._i]
        self._i += 1
        content = [
            self._ns(type="tool_use", id=f"t{self._i}_{j}", name=name, input=args)
            for j, (name, args) in enumerate(turn)
        ]
        return self._ns(content=content, stop_reason="tool_use")


def default_client() -> LLMClient | None:
    """A real client if credentials are configured, else ``None`` so callers can
    fall back (the orchestrator requires an explicit client in tests)."""
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return AnthropicClient()
    return None
