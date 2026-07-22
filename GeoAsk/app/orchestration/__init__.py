"""Phase 2 — the AI orchestration layer.

Translates a plain-English question into a chain of Phase 1 primitive calls via
LLM function calling. The model only ever calls the validated tools and only
ever sees layer handles + summaries, never raw geometry.
"""

from .orchestrator import AskResult, TraceStep, ask
from .sources import DataSource, InMemoryDataSource, PostgisDataSource

__all__ = [
    "ask",
    "AskResult",
    "TraceStep",
    "DataSource",
    "InMemoryDataSource",
    "PostgisDataSource",
]
