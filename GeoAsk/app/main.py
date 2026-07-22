"""GeoAsk API + frontend entry point.

Exposes the deterministic spatial-primitive layer (Phase 1), the AI
orchestration layer (Phase 2, ``/ask``), and serves the map + chat frontend
(Phase 3) as static files. Run locally with:

    uvicorn app.main:app --reload   # UI at http://localhost:8000/
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import ask, primitives

_WEB_DIR = Path(__file__).resolve().parent / "web"

app = FastAPI(
    title="GeoAsk",
    version="0.3.0",
    summary="Natural-language-to-map engine — primitives + AI orchestration + map/chat UI",
)

app.include_router(primitives.router)
app.include_router(ask.router)

# Static assets (JS/CSS) for the frontend.
app.mount("/static", StaticFiles(directory=_WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(_WEB_DIR / "index.html")


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "primitives": [r.path for r in primitives.router.routes]}
