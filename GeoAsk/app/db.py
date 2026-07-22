"""PostGIS connection management.

Thin wrapper over psycopg. The connection string comes from ``DATABASE_URL``
(see ``.env.example`` / docker-compose). Kept separate from the data-access
queries so the queries can be unit-tested against a fake cursor without a live
database.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import psycopg

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


@contextmanager
def connect(url: str | None = None) -> Iterator["psycopg.Connection"]:
    conn = psycopg.connect(url or database_url())
    try:
        yield conn
    finally:
        conn.close()


def apply_schema(conn: "psycopg.Connection") -> None:
    """Create the PostGIS extension, tables and indexes (idempotent)."""
    conn.execute(_SCHEMA_PATH.read_text())
    conn.commit()
