"""GeoAsk API entry point.

Right now this exposes the deterministic spatial-primitive layer (Phase 1). The
AI orchestration layer (Phase 2) will mount here too, calling these same
endpoints via their tool schemas — it will not gain any privileged path to the
data. Run locally with:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI

from .routers import ask, primitives

app = FastAPI(
    title="GeoAsk",
    version="0.2.0",
    summary="Natural-language-to-map engine — primitives + AI orchestration",
)

app.include_router(primitives.router)
app.include_router(ask.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "primitives": [r.path for r in primitives.router.routes]}
