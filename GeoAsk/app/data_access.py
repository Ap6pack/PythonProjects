"""Data access: PostGIS rows -> GeoJSON FeatureCollections.

This is the layer the caveat was about. The primitives operate on GeoJSON; this
module is what turns real PostGIS tables into that GeoJSON, so the same tested
primitive functions run against live data. Geometry is serialised in the
database with ``ST_AsGeoJSON`` and the feature envelope is assembled in Python,
which keeps the SQL simple and the row->feature mapping easy to unit-test.

The query builders are separated from execution (``_fetch``) so the SQL and the
FeatureCollection assembly can be tested against a fake cursor with no database.
"""

from __future__ import annotations

import json
from typing import Any, Iterable, Sequence


def _feature_from_row(row: Sequence[Any], property_names: Sequence[str]) -> dict[str, Any]:
    """A row is (geojson_geometry_text, *property_values)."""
    geometry = json.loads(row[0])
    properties = {name: row[i + 1] for i, name in enumerate(property_names)}
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def _collection(rows: Iterable[Sequence[Any]], property_names: Sequence[str]) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [_feature_from_row(r, property_names) for r in rows],
    }


def _fetch(conn, sql: str, params: Sequence[Any]) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# --- POIs --------------------------------------------------------------------

_POI_PROPS = ["category", "name"]
_POI_SQL = """
    SELECT ST_AsGeoJSON(geom), category, name
    FROM pois
    WHERE category = %s
"""


def pois_by_category(conn, category: str) -> dict[str, Any]:
    rows = _fetch(conn, _POI_SQL, (category,))
    return _collection(rows, _POI_PROPS)


# --- Tracts ------------------------------------------------------------------

_TRACT_PROPS = ["geoid", "population", "pct_senior", "median_income"]
_TRACT_SQL = """
    SELECT ST_AsGeoJSON(geom), geoid, population, pct_senior, median_income
    FROM tracts
"""


def all_tracts(conn) -> dict[str, Any]:
    rows = _fetch(conn, _TRACT_SQL, ())
    return _collection(rows, _TRACT_PROPS)


# --- Phase 0 acceptance query ------------------------------------------------

_TRACTS_NEAR_CATEGORY_SQL = """
    SELECT ST_AsGeoJSON(t.geom), t.geoid, t.population, t.pct_senior, t.median_income
    FROM tracts t
    WHERE EXISTS (
        SELECT 1 FROM pois p
        WHERE p.category = %s
          AND ST_DWithin(t.geom::geography, p.geom::geography, %s)
    )
"""


def tracts_within_of_category(conn, category: str, meters: float) -> dict[str, Any]:
    """Tracts within ``meters`` of any POI of ``category`` — the Phase 0
    acceptance query, returned as GeoJSON ready for the primitives."""
    rows = _fetch(conn, _TRACTS_NEAR_CATEGORY_SQL, (category, meters))
    return _collection(rows, _TRACT_PROPS)
