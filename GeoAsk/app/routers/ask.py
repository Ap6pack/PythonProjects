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


class AskResponse(BaseModel):
    finished: bool
    explanation: str
    geojson: dict[str, Any] | None
    trace: list[TraceStepModel]


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

    return AskResponse(
        finished=result.finished,
        explanation=result.explanation,
        geojson=result.geojson,
        trace=[TraceStepModel(tool=s.tool, args=s.args, result=s.result, is_error=s.is_error)
               for s in result.trace],
    )
