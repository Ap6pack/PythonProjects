"""nearest — for each source feature, the closest destination and its distance.

Answers "how far is each neighbourhood from the nearest pharmacy". Distance is
straight-line metres in the local metric projection; road-network distance is a
future upgrade that swaps the metric for a routing call without changing this
signature.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import shape
from shapely.strtree import STRtree

from .geo import (
    centroid_lonlat,
    feature_collection,
    features_of,
    make_projectors,
)


def nearest(source: dict[str, Any], destinations: dict[str, Any]) -> dict[str, Any]:
    """Attach ``_nearest_distance_m`` (and any destination properties, prefixed
    ``nearest_``) to every source feature."""
    dest_features = [f for f in features_of(destinations) if f.get("geometry")]
    if not dest_features:
        raise ValueError("destinations collection is empty")

    # Centre the metric projection on the combined data so both layers share it.
    lon, lat = centroid_lonlat(_combine(source, destinations))
    to_metric, _ = make_projectors(lon, lat)

    dest_geoms = [to_metric(shape(f["geometry"])) for f in dest_features]
    tree = STRtree(dest_geoms)

    out = []
    for f in features_of(source):
        if not f.get("geometry"):
            continue
        geom = to_metric(shape(f["geometry"]))
        idx = int(tree.nearest(geom))
        distance = geom.distance(dest_geoms[idx])
        props = dict(f.get("properties") or {})
        props["_nearest_distance_m"] = round(distance, 3)
        for k, v in (dest_features[idx].get("properties") or {}).items():
            props[f"nearest_{k}"] = v
        out.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return feature_collection(out)


def _combine(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    return feature_collection(features_of(a) + features_of(b))
