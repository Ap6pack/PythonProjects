"""Data sources the orchestration layer can load base layers from.

The tools that fetch data (``load_pois``, ``load_tracts``) go through a
``DataSource`` protocol rather than talking to PostGIS directly. That keeps the
orchestrator testable with an in-memory source (no database) and lets the same
tool code run against real PostGIS in production — the primitives never change,
only where the GeoJSON originates.
"""

from __future__ import annotations

from typing import Any, Protocol


class DataSource(Protocol):
    def load_pois(self, category: str) -> dict[str, Any]:
        """POIs of a category as a GeoJSON FeatureCollection."""
        ...

    def load_tracts(self) -> dict[str, Any]:
        """Census tracts as a GeoJSON FeatureCollection."""
        ...


class InMemoryDataSource:
    """Fixed FeatureCollections keyed by POI category, for demos and tests."""

    def __init__(self, pois_by_category: dict[str, dict[str, Any]], tracts: dict[str, Any]):
        self._pois = pois_by_category
        self._tracts = tracts

    def load_pois(self, category: str) -> dict[str, Any]:
        return self._pois.get(category, {"type": "FeatureCollection", "features": []})

    def load_tracts(self) -> dict[str, Any]:
        return self._tracts


class PostgisDataSource:
    """Loads base layers from PostGIS via the data-access module."""

    def __init__(self, conn):
        self._conn = conn

    def load_pois(self, category: str) -> dict[str, Any]:
        from .. import data_access

        return data_access.pois_by_category(self._conn, category)

    def load_tracts(self) -> dict[str, Any]:
        from .. import data_access

        return data_access.all_tracts(self._conn)
