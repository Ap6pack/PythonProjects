"""Orchestration-layer tests, driven by a scripted fake LLM (no API key).

The fake plays a fixed list of turns, each a list of (tool_name, args) calls,
exactly as the real model's tool_use blocks would arrive. Because layer handles
are assigned deterministically (layer_1, layer_2, …), the scripts can reference
them — the same way the model references the handles it got back.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.orchestration import InMemoryDataSource, ask


# --- fake LLM client ---------------------------------------------------------

def _tool_use(call_id, name, args):
    return SimpleNamespace(type="tool_use", id=call_id, name=name, input=args)


class ScriptedLLM:
    """Plays scripted turns; records the messages it is handed each call."""

    def __init__(self, turns):
        self._turns = turns
        self._i = 0
        self.seen_messages = []

    def respond(self, system, tools, messages):
        self.seen_messages.append(messages)
        turn = self._turns[self._i]
        self._i += 1
        content = [_tool_use(f"t{self._i}_{j}", name, args) for j, (name, args) in enumerate(turn)]
        return SimpleNamespace(content=content, stop_reason="tool_use")


# --- fixtures ----------------------------------------------------------------

LON, LAT = -122.68, 45.52


def _point(lon, lat, **props):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def _tract(name, x0, y0, size, **props):
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": {"tract": name, **props}}


@pytest.fixture
def source():
    pharmacies = {"type": "FeatureCollection", "features": [_point(LON, LAT, name="Central")]}
    tracts = {
        "type": "FeatureCollection",
        "features": [
            _tract("near-young", LON - 0.01, LAT - 0.01, 0.02, pct_senior=8.0),
            _tract("far-senior", LON + 0.20, LAT, 0.02, pct_senior=27.0),
            _tract("far-young", LON + 0.20, LAT + 0.03, 0.02, pct_senior=9.0),
        ],
    }
    return InMemoryDataSource({"pharmacy": pharmacies}, tracts)


# --- the headline test: a full access-gap chain ------------------------------

def test_full_access_gap_chain(source):
    turns = [
        [("load_pois", {"category": "pharmacy"})],                                  # layer_1
        [("isochrone", {"layer_id": "layer_1", "minutes": 10, "mode": "drive"})],   # layer_2
        [("load_tracts", {})],                                                      # layer_3
        [("spatial_join", {"target_layer_id": "layer_3", "join_layer_id": "layer_2",
                            "predicate": "intersects", "keep": "non_matching"})],    # layer_4
        [("filter_by_attribute", {"layer_id": "layer_4", "attribute": "pct_senior",
                                   "op": ">", "value": 15})],                        # layer_5
        [("finish", {"layer_id": "layer_5", "explanation": "Found pharmacies, built "
                     "10-min drive areas, took tracts outside them, kept the senior ones."})],
    ]
    result = ask("neighbourhoods >10 min from a pharmacy with many seniors", ScriptedLLM(turns), source)

    assert result.finished
    names = [f["properties"]["tract"] for f in result.geojson["features"]]
    assert names == ["far-senior"]
    assert "drive" in result.explanation
    # The trace is the transparency panel: one step per executed tool + finish.
    assert [s.tool for s in result.trace] == [
        "load_pois", "isochrone", "load_tracts", "spatial_join", "filter_by_attribute", "finish"
    ]


# --- guardrails --------------------------------------------------------------

def test_error_is_reported_then_repaired(source):
    turns = [
        [("load_pois", {"category": "pharmacy"})],                       # layer_1
        [("buffer", {"layer_id": "layer_1", "distance_m": -5})],          # error, no layer
        [("buffer", {"layer_id": "layer_1", "distance_m": 500})],         # layer_2 (repaired)
        [("finish", {"layer_id": "layer_2", "explanation": "buffered"})],
    ]
    result = ask("within 500m of a pharmacy", ScriptedLLM(turns), source)
    assert result.finished
    errored = [s for s in result.trace if s.is_error]
    assert len(errored) == 1 and "distance_m must be positive" in errored[0].result["error"]


def test_finish_with_bad_layer_is_rejected_not_crashed(source):
    turns = [
        [("load_pois", {"category": "pharmacy"})],                        # layer_1
        [("finish", {"layer_id": "layer_99", "explanation": "oops"})],    # bad handle
        [("finish", {"layer_id": "layer_1", "explanation": "ok"})],       # valid
    ]
    result = ask("show pharmacies", ScriptedLLM(turns), source)
    assert result.finished
    assert len(result.geojson["features"]) == 1


def test_unknown_layer_reference_is_an_error(source):
    turns = [
        [("buffer", {"layer_id": "layer_1", "distance_m": 100})],  # nothing loaded yet
        [("load_pois", {"category": "pharmacy"})],                 # now layer_1 exists
        [("finish", {"layer_id": "layer_1", "explanation": "done"})],
    ]
    result = ask("q", ScriptedLLM(turns), source)
    assert result.trace[0].is_error
    assert "no such layer" in result.trace[0].result["error"]


# --- the design rule: the model never receives raw geometry ------------------

def test_llm_never_sees_coordinates(source):
    turns = [
        [("load_pois", {"category": "pharmacy"})],
        [("finish", {"layer_id": "layer_1", "explanation": "done"})],
    ]
    llm = ScriptedLLM(turns)
    ask("show pharmacies", llm, source)

    # Everything handed to the LLM (tool results included) must be geometry-free.
    blob = json.dumps(_serialisable(llm.seen_messages))
    assert "coordinates" not in blob
    assert "feature_count" in blob  # it did get the summary


def _serialisable(messages):
    """Keep only what actually carries data to the model: the initial question
    string and the tool_result blocks. Assistant turns hold SimpleNamespace
    blocks (the fake's stand-in for SDK objects) and aren't model *input*."""
    out = []
    for msg_list in messages:
        for m in msg_list:
            content = m.get("content")
            if isinstance(content, str):
                out.append(content)
            elif isinstance(content, list):
                out.extend(b for b in content if isinstance(b, dict) and b.get("type") == "tool_result")
    return out
