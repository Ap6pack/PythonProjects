"""The /ask endpoint — plain-English question in, map + transparency out.

This is the product surface: a non-technical user's question goes to the
orchestration layer, which drives the primitives via LLM function calling and
returns the answer layer as GeoJSON plus the step-by-step trace for the
transparency panel.

Requires a configured LLM (ANTHROPIC_API_KEY) and a PostGIS connection
(DATABASE_URL); returns 503 if either is missing rather than pretending.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import db
from ..orchestration import PostgisDataSource, ask
from ..orchestration.llm import default_client

router = APIRouter(prefix="/ask", tags=["orchestration"])


class AskRequest(BaseModel):
    question: str


class TraceStepModel(BaseModel):
    tool: str
    args: dict[str, Any]
    result: dict[str, Any]
    is_error: bool


class ClarificationModel(BaseModel):
    question: str
    options: list[str]


class AskResponse(BaseModel):
    finished: bool
    explanation: str
    geojson: dict[str, Any] | None
    trace: list[TraceStepModel]
    clarification: ClarificationModel | None = None


def _to_response(result) -> "AskResponse":
    return AskResponse(
        finished=result.finished,
        explanation=result.explanation,
        geojson=result.geojson,
        trace=[TraceStepModel(tool=s.tool, args=s.args, result=s.result, is_error=s.is_error)
               for s in result.trace],
        clarification=(
            ClarificationModel(question=result.clarification.question,
                               options=result.clarification.options)
            if result.clarification else None
        ),
    )


@router.post("/demo", response_model=AskResponse)
def ask_demo(variant: str = "gap"):
    """Run the orchestrator over in-memory sample data with a scripted planner —
    no API key or database needed. Lets the frontend be demoed end-to-end.
    ``variant='clarify'`` shows the ask-a-follow-up flow."""
    from ..orchestration.demo import run_clarify_demo, run_demo

    result = run_clarify_demo() if variant == "clarify" else run_demo()
    return _to_response(result)


@router.post("", response_model=AskResponse)
def ask_question(req: AskRequest):
    client = default_client()
    if client is None:
        raise HTTPException(503, "LLM not configured (set ANTHROPIC_API_KEY)")
    try:
        url = db.database_url()
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc

    with db.connect(url) as conn:
        result = ask(req.question, client, PostgisDataSource(conn))

    return _to_response(result)
