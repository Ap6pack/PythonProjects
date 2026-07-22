"""The layer store — the enforcement point for "the LLM never touches raw data".

Every spatial result lives here as a GeoJSON FeatureCollection keyed by an
opaque handle (``layer_1``, ``layer_2``, …). The LLM only ever sees a *summary*
of a layer (feature count, geometry type, property names, a couple of sample
values) — never the coordinates. It chains operations by passing handles
between tools. This keeps the model's context small and cheap, and means a
malformed model output can never corrupt the underlying data: the worst it can
do is name a handle that doesn't exist, which the executor rejects.
"""

from __future__ import annotations

import itertools
from typing import Any

from ..spatial.geo import features_of


class LayerStore:
    def __init__(self) -> None:
        self._layers: dict[str, dict[str, Any]] = {}
        self._counter = itertools.count(1)

    def add(self, fc: dict[str, Any]) -> str:
        """Store a FeatureCollection and return its new handle."""
        layer_id = f"layer_{next(self._counter)}"
        self._layers[layer_id] = fc
        return layer_id

    def get(self, layer_id: str) -> dict[str, Any]:
        if layer_id not in self._layers:
            raise KeyError(layer_id)
        return self._layers[layer_id]

    def summary(self, layer_id: str) -> dict[str, Any]:
        """A compact, geometry-free description for the LLM."""
        fc = self.get(layer_id)
        feats = features_of(fc)
        geom_type = None
        props: dict[str, Any] = {}
        if feats:
            geom = feats[0].get("geometry") or {}
            geom_type = geom.get("type")
            props = feats[0].get("properties") or {}
        return {
            "layer_id": layer_id,
            "feature_count": len(feats),
            "geometry_type": geom_type,
            # Property names plus one sample value each, so the model knows what
            # it can filter or overlay on — without shipping every row.
            "properties": {k: props[k] for k in list(props)[:12]},
        }
