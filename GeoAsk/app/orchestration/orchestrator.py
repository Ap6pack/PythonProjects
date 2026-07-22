"""The orchestration loop: plain-English question -> chain of primitive calls.

Runs a manual tool-use loop (chosen over the SDK tool runner so the whole thing
stays driven by the injected ``LLMClient`` protocol and is testable with a
scripted fake). On each turn the model either calls tools or finishes:

    parse  -> the model reads the question + tool results so far
    plan   -> it emits tool_use blocks (which tools, what order)
    execute-> ToolExecutor runs them against the primitives; errors come back as
              is_error results the model can repair
    assemble-> when it calls ``finish``, we return that layer's GeoJSON, the
              model's plain-English explanation, and the full step-by-step trace

The trace is the transparency panel the plan calls non-negotiable: every tool
call and its geometry-free result, in order.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .layers import LayerStore
from .llm import LLMClient
from .sources import DataSource
from .tools import TOOL_SCHEMAS, ToolExecutor

SYSTEM_PROMPT = """You are the planning engine of GeoAsk, a natural-language-to-map tool.

You answer spatial questions by calling a fixed set of validated spatial tools.
You never see or handle raw geometry — every tool takes and returns opaque layer
handles (e.g. "layer_3") plus a summary (feature count, property names). Chain
tools by passing handles between them.

SCOPE: the MVP answers ACCESS-GAP questions — "which neighbourhoods are poorly
served by / far from <facility>, optionally among <demographic>". Users phrase
this many ways; they all map to the same recipe. Treat all of these as the
access-gap pattern:
  - "neighbourhoods more than 10 minutes from a pharmacy"
  - "where are the pharmacy deserts / gaps in pharmacy access"
  - "areas underserved by pharmacies, especially with lots of seniors"
  - "show tracts that can't reach a pharmacy within a 10-minute drive"
  - "which communities have poor access to pharmacies and older residents"

CANONICAL RECIPE (access gap by travel time, optionally filtered by demographic):
  1. load_pois(category)                     -> the facilities
  2. isochrone(facilities, minutes, mode)    -> reachable areas
  3. load_tracts()                           -> the neighbourhoods
  4. spatial_join(target=tracts, join=areas, keep="non_matching")
                                             -> tracts outside every area (the gap)
  5. (optional) filter_by_attribute or demographic_overlay for the demographic
  6. finish(final_layer, explanation)

Pick sensible defaults when the user is vague: 10 minutes, drive mode. For
"above average <field>", a reasonable threshold on that field is fine — say so in
the explanation. Only use property names a layer's summary actually reports. If a
tool returns an error, read it and correct your next call.

If a question is clearly NOT an access-gap question (e.g. routing, geocoding,
unrelated), briefly say it's outside the current MVP scope instead of forcing a
chain. Otherwise, when the answer layer is ready, call finish — do not stop
without calling it, and write the explanation for a non-technical reader."""


@dataclass
class TraceStep:
    tool: str
    args: dict[str, Any]
    result: dict[str, Any]
    is_error: bool


@dataclass
class AskResult:
    geojson: dict[str, Any] | None
    explanation: str
    trace: list[TraceStep] = field(default_factory=list)
    finished: bool = False


def ask(
    question: str,
    client: LLMClient,
    source: DataSource,
    *,
    max_turns: int = 12,
) -> AskResult:
    store = LayerStore()
    executor = ToolExecutor(store, source)
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    trace: list[TraceStep] = []

    for _ in range(max_turns):
        response = client.respond(SYSTEM_PROMPT, TOOL_SCHEMAS, messages)
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [b for b in response.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            # Model answered in prose without producing a map.
            return AskResult(
                geojson=None,
                explanation=_text_of(response.content),
                trace=trace,
                finished=False,
            )

        tool_results = []
        for block in tool_uses:
            if block.name == "finish":
                layer_id = block.input.get("layer_id")
                explanation = block.input.get("explanation", "")
                try:
                    geojson = store.get(layer_id)
                except KeyError:
                    # Guardrail: finish named a non-existent layer — tell the
                    # model so it can pick a real one instead of failing.
                    tool_results.append(_error_result(block.id, f"no such layer: {layer_id}"))
                    continue
                trace.append(TraceStep("finish", dict(block.input), {"layer_id": layer_id}, False))
                return AskResult(geojson=geojson, explanation=explanation, trace=trace, finished=True)

            result, is_error = executor.execute(block.name, block.input)
            trace.append(TraceStep(block.name, dict(block.input), result, is_error))
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": _to_text(result),
                    "is_error": is_error,
                }
            )

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return AskResult(
        geojson=None,
        explanation="Stopped: the plan did not converge within the step budget.",
        trace=trace,
        finished=False,
    )


def _to_text(result: dict[str, Any]) -> str:
    import json

    return json.dumps(result)


def _error_result(tool_use_id: str, message: str) -> dict[str, Any]:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": message,
        "is_error": True,
    }


def _text_of(content: Any) -> str:
    parts = [getattr(b, "text", "") for b in content if getattr(b, "type", None) == "text"]
    return " ".join(p for p in parts if p).strip()
