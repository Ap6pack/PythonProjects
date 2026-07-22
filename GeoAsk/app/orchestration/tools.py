"""Tool schemas for LLM function calling, and the executor that runs them.

The schemas mirror the Phase 1 primitives (and the two data-loading entry
points) so the model plans in terms of the exact validated operations the engine
supports — it cannot invent an operation, and it cannot pass raw geometry. Every
tool takes/returns layer handles (see ``layers.py``).

The executor is the validation guardrail: it confirms referenced handles exist,
dispatches to the pure primitive, and turns any ``ValueError`` (bad distance,
unknown operator, empty layer) into an ``is_error`` tool result so the model can
repair its own call instead of the whole request failing.
"""

from __future__ import annotations

from typing import Any

from .. import spatial
from .layers import LayerStore
from .sources import DataSource

# --- schemas presented to the model ------------------------------------------

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "load_pois",
        "description": (
            "Load points of interest of a given category (e.g. 'pharmacy', "
            "'school', 'grocery') as a new layer. Start here to get the "
            "facilities a question is about."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"category": {"type": "string"}},
            "required": ["category"],
        },
    },
    {
        "name": "load_tracts",
        "description": (
            "Load census tracts (with population, pct_senior, median_income) as "
            "a new layer. Use for the neighbourhoods/areas a question asks about."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "isochrone",
        "description": (
            "Build travel-time reachable areas around each feature of a layer. "
            "Returns a new polygon layer."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "layer_id": {"type": "string"},
                "minutes": {"type": "number"},
                "mode": {"type": "string", "enum": ["walk", "bike", "drive"]},
            },
            "required": ["layer_id", "minutes"],
        },
    },
    {
        "name": "buffer",
        "description": "Grow each feature of a layer by a distance in metres. Returns a new polygon layer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "layer_id": {"type": "string"},
                "distance_m": {"type": "number"},
            },
            "required": ["layer_id", "distance_m"],
        },
    },
    {
        "name": "spatial_join",
        "description": (
            "Relate a target layer to a join layer by a topological predicate. "
            "keep='non_matching' returns the target features NOT related to any "
            "join feature — that is the access gap (e.g. tracts outside every "
            "drive-time area)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target_layer_id": {"type": "string"},
                "join_layer_id": {"type": "string"},
                "predicate": {"type": "string", "enum": ["intersects", "within", "contains"]},
                "keep": {"type": "string", "enum": ["matching", "non_matching"]},
            },
            "required": ["target_layer_id", "join_layer_id"],
        },
    },
    {
        "name": "filter_by_attribute",
        "description": "Keep only features whose property passes a comparison. Returns a new layer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "layer_id": {"type": "string"},
                "attribute": {"type": "string"},
                "op": {"type": "string", "enum": ["==", "!=", ">", ">=", "<", "<="]},
                "value": {"description": "Number, string, or boolean to compare against"},
            },
            "required": ["layer_id", "attribute", "op", "value"],
        },
    },
    {
        "name": "demographic_overlay",
        "description": (
            "Area-weighted aggregation of a tract value onto areas. kind='extensive' "
            "for counts (population), 'intensive' for rates (pct_senior). Returns "
            "the areas layer with the value attached."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "areas_layer_id": {"type": "string"},
                "tracts_layer_id": {"type": "string"},
                "value_field": {"type": "string"},
                "kind": {"type": "string", "enum": ["extensive", "intensive"]},
                "out_field": {"type": "string"},
            },
            "required": ["areas_layer_id", "tracts_layer_id", "value_field"],
        },
    },
    {
        "name": "nearest",
        "description": (
            "For each feature of a source layer, attach the distance in metres to "
            "the nearest destination-layer feature. Returns the source layer "
            "annotated with _nearest_distance_m."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_layer_id": {"type": "string"},
                "destinations_layer_id": {"type": "string"},
            },
            "required": ["source_layer_id", "destinations_layer_id"],
        },
    },
    {
        "name": "clarify",
        "description": (
            "Ask the user one short follow-up question when the request is "
            "genuinely ambiguous and a wrong guess would produce a misleading "
            "map — e.g. the facility type is unclear, or a consequential choice "
            "(walk vs drive in a context where it matters) is unstated. Provide "
            "2-4 concrete options. Prefer sensible defaults over clarifying; only "
            "use this when defaulting is genuinely risky."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "options": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["question", "options"],
        },
    },
    {
        "name": "finish",
        "description": (
            "Call when the answer layer is ready. Provide the final layer_id and a "
            "one-paragraph plain-English explanation of what the engine did, step "
            "by step, for the transparency panel."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "layer_id": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["layer_id", "explanation"],
        },
    },
]


class ToolExecutor:
    """Runs a single tool call against the primitives and the layer store."""

    def __init__(self, store: LayerStore, source: DataSource):
        self.store = store
        self.source = source

    def execute(self, name: str, args: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        """Return (result, is_error). ``result`` is JSON-safe and geometry-free."""
        try:
            handler = getattr(self, f"_{name}", None)
            if handler is None:
                return {"error": f"unknown tool {name!r}"}, True
            return handler(args), False
        except KeyError as exc:
            return {"error": f"no such layer: {exc}"}, True
        except ValueError as exc:
            return {"error": str(exc)}, True

    # data loading -----------------------------------------------------------

    def _load_pois(self, a):
        fc = self.source.load_pois(a["category"])
        return self._store_summary(fc)

    def _load_tracts(self, a):
        return self._store_summary(self.source.load_tracts())

    # primitives -------------------------------------------------------------

    def _isochrone(self, a):
        fc = self.store.get(a["layer_id"])
        out = spatial.isochrone(fc, a["minutes"], a.get("mode", "drive"))
        return self._store_summary(out)

    def _buffer(self, a):
        out = spatial.buffer(self.store.get(a["layer_id"]), a["distance_m"])
        return self._store_summary(out)

    def _spatial_join(self, a):
        out = spatial.spatial_join(
            self.store.get(a["target_layer_id"]),
            self.store.get(a["join_layer_id"]),
            a.get("predicate", "intersects"),
            a.get("keep", "matching"),
        )
        return self._store_summary(out)

    def _filter_by_attribute(self, a):
        out = spatial.filter_by_attribute(
            self.store.get(a["layer_id"]), a["attribute"], a["op"], a["value"]
        )
        return self._store_summary(out)

    def _demographic_overlay(self, a):
        out = spatial.demographic_overlay(
            self.store.get(a["areas_layer_id"]),
            self.store.get(a["tracts_layer_id"]),
            a["value_field"],
            a.get("kind", "extensive"),
            a.get("out_field"),
        )
        return self._store_summary(out)

    def _nearest(self, a):
        out = spatial.nearest(
            self.store.get(a["source_layer_id"]), self.store.get(a["destinations_layer_id"])
        )
        return self._store_summary(out)

    # helper -----------------------------------------------------------------

    def _store_summary(self, fc: dict[str, Any]) -> dict[str, Any]:
        return self.store.summary(self.store.add(fc))
