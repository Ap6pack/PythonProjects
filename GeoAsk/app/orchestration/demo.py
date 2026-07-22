"""A no-config demo of the orchestration layer.

Runs the real orchestrator — layer store, executor, guardrails, transparency
trace — over a small but realistic Portland-area sample (two pharmacies, seven
census tracts) using a scripted planner instead of a live LLM. It produces a
genuine access-gap result and trace, so the frontend can be shown working
without an API key or database. The planning is canned; everything downstream is
real, and the sample is sized so the answer is a handful of tracts, not one.
"""

from __future__ import annotations

from typing import Any

from .llm import ScriptedClient
from .orchestrator import AskResult, ask
from .sources import InMemoryDataSource


def _point(lon, lat, **props):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def _tract(name, x0, y0, **props):
    size = 0.02
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [ring]},
        "properties": {"tract": name, **props},
    }


def _sample_source() -> InMemoryDataSource:
    pharmacies = {
        "type": "FeatureCollection",
        "features": [
            _point(-122.68, 45.52, name="Central Pharmacy"),
            _point(-122.61, 45.52, name="Eastside Pharmacy"),
        ],
    }
    tracts = {
        "type": "FeatureCollection",
        "features": [
            # Near the pharmacies (reachable) — excluded from the access gap.
            _tract("Sellwood",    -122.69, 45.51, population=1500, pct_senior=8.0),
            _tract("Richmond",    -122.66, 45.52, population=1800, pct_senior=22.0),
            _tract("Montavilla",  -122.62, 45.50, population=1200, pct_senior=12.0),
            # Far from any pharmacy — the access gap.
            _tract("Pleasant Vly", -122.42, 45.52, population=1400, pct_senior=27.0),
            _tract("Powellhurst",  -122.42, 45.55, population=1100, pct_senior=19.0),
            _tract("Centennial",   -122.45, 45.49, population=1600, pct_senior=9.0),
            _tract("Hazelwood",    -122.39, 45.53, population=1300, pct_senior=24.0),
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
                 "I found the pharmacies, built 10-minute drive-time areas around them, "
                 "selected the neighbourhoods that fall outside every drive-time area, "
                 "and kept the ones with an above-average senior population."})],
]


# An ambiguous question the model can't safely default — it asks which facility.
_CLARIFY_PLAN: list[list[tuple[str, dict[str, Any]]]] = [
    [("clarify", {"question": "Which facilities do you mean?",
                  "options": ["Pharmacies", "Grocery stores", "Schools"]})],
]


def run_demo() -> AskResult:
    return ask("sample question", ScriptedClient(_PLAN), _sample_source())


# A refinement of the gap result: tighten the senior threshold to 20% — narrows
# the 3 gap tracts to 2 (Powellhurst at 19% drops out).
_REFINE_PLAN: list[list[tuple[str, dict[str, Any]]]] = [
    [("load_pois", {"category": "pharmacy"})],
    [("isochrone", {"layer_id": "layer_1", "minutes": 10, "mode": "drive"})],
    [("load_tracts", {})],
    [("spatial_join", {"target_layer_id": "layer_3", "join_layer_id": "layer_2",
                       "predicate": "intersects", "keep": "non_matching"})],
    [("filter_by_attribute", {"layer_id": "layer_4", "attribute": "pct_senior", "op": ">", "value": 20})],
    [("finish", {"layer_id": "layer_5", "explanation":
                 "Refined to neighbourhoods where seniors are more than 20% of the "
                 "population — a stricter cut of the same access gap."})],
]


def run_clarify_demo() -> AskResult:
    return ask("underserved areas", ScriptedClient(_CLARIFY_PLAN), _sample_source())


def run_refine_demo() -> AskResult:
    return ask("only the ones with more than 20% seniors", ScriptedClient(_REFINE_PLAN), _sample_source())
