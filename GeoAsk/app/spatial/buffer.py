"""buffer — grow each feature by a fixed distance in metres.

Used on its own ("everything within 500 m of a school") and as a building block
for the approximate isochrone. Distances are metric: the geometries are
reprojected to a local AEQD projection, buffered, and reprojected back to WGS84.
"""

from __future__ import annotations

from typing import Any

from .geo import (
    centroid_lonlat,
    feature,
    feature_collection,
    features_of,
    make_projectors,
)
from shapely.geometry import shape


def buffer(fc: dict[str, Any], distance_m: float) -> dict[str, Any]:
    """Buffer every feature in ``fc`` by ``distance_m`` metres.

    Properties are carried through unchanged. A non-positive distance is an
    error rather than a silent shrink, because callers upstream (the LLM tool
    layer) should never pass one and it almost always signals a unit mix-up.
    """
    if distance_m <= 0:
        raise ValueError("distance_m must be positive")

    lon, lat = centroid_lonlat(fc)
    to_metric, to_wgs = make_projectors(lon, lat)

    out = []
    for f in features_of(fc):
        if not f.get("geometry"):
            continue
        geom_m = to_metric(shape(f["geometry"]))
        buffered = to_wgs(geom_m.buffer(distance_m))
        out.append(feature(buffered, f.get("properties")))
    return feature_collection(out)
