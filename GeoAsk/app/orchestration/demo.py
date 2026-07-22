"""A no-config demo of the orchestration layer.

Runs the real orchestrator — layer store, executor, guardrails, transparency
trace — over small in-memory sample data (a Portland-area pharmacy and three
tracts) using a scripted planner instead of a live LLM. It produces a genuine
access-gap result and trace, so the frontend can be seen working without an API
key or database. The planning is canned; everything downstream is real.
"""

from __future__ import annotations

from typing import Any

from .llm import ScriptedClient
from .orchestrator import AskResult, ask
from .sources import InMemoryDataSource

LON, LAT = -122.68, 45.52


def _point(lon, lat, **props):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def _tract(name, x0, y0, size, **props):
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [ring]},
        "properties": {"tract": name, **props},
    }


def _sample_source() -> InMemoryDataSource:
    pharmacies = {"type": "FeatureCollection", "features": [_point(LON, LAT, name="Central Pharmacy")]}
    tracts = {
        "type": "FeatureCollection",
        "features": [
            _tract("near-young", LON - 0.01, LAT - 0.01, 0.02, population=1500, pct_senior=8.0),
            _tract("far-senior", LON + 0.20, LAT, 0.02, population=1200, pct_senior=27.0),
            _tract("far-young", LON + 0.20, LAT + 0.03, 0.02, population=1800, pct_senior=9.0),
        ],
    }
    return InMemoryDataSource({"pharmacy": pharmacies}, tracts)


# The canned plan for: "neighbourhoods >10 min from a pharmacy with above-average
# seniors" — the same chain a live model produces for this question type.
_PLAN: list[list[tuple[str, dict[str, Any]]]] = [
    [("load_pois", {"category": "pharmacy"})],
    [("isochrone", {"layer_id": "layer_1", "minutes": 10, "mode": "drive"})],
    [("load_tracts", {})],
    [("spatial_join", {"target_layer_id": "layer_3", "join_layer_id": "layer_2",
                       "predicate": "intersects", "keep": "non_matching"})],
    [("filter_by_attribute", {"layer_id": "layer_4", "attribute": "pct_senior", "op": ">", "value": 15})],
    [("finish", {"layer_id": "layer_5", "explanation":
                 "I found pharmacies, built 10-minute drive-time areas around them, "
                 "selected the neighbourhoods that fall outside every drive-time area, "
                 "and kept the ones with an above-average senior population."})],
]


def run_demo() -> AskResult:
    return ask("sample question", ScriptedClient(_PLAN), _sample_source())
