"""demographic_overlay — area-weighted aggregation of tract values onto areas.

Census values live on tracts, but questions are asked about arbitrary areas
(drive-time zones, buffers, neighbourhoods). This apportions a tract's value to
an area by the fraction of the tract's area that falls inside it — the standard
areal-interpolation assumption of uniform density within a tract.

Two value kinds:

* ``extensive`` (counts — population, households): apportioned by area fraction
  and summed. A tract 30% inside an area contributes 30% of its people.
* ``intensive`` (rates/densities — median income, % seniors): combined as an
  area-weighted mean instead of summed.
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


def demographic_overlay(
    areas: dict[str, Any],
    tracts: dict[str, Any],
    value_field: str,
    kind: str = "extensive",
    out_field: str | None = None,
) -> dict[str, Any]:
    if kind not in {"extensive", "intensive"}:
        raise ValueError("kind must be 'extensive' or 'intensive'")
    out_field = out_field or value_field

    tract_features = [f for f in features_of(tracts) if f.get("geometry")]
    if not tract_features:
        raise ValueError("tracts collection is empty")

    lon, lat = centroid_lonlat(_combine(areas, tracts))
    to_metric, _ = make_projectors(lon, lat)

    tract_geoms = [to_metric(shape(f["geometry"])) for f in tract_features]
    tract_vals = [_num((f.get("properties") or {}).get(value_field)) for f in tract_features]
    tract_areas = [g.area for g in tract_geoms]
    tree = STRtree(tract_geoms)

    out = []
    for f in features_of(areas):
        if not f.get("geometry"):
            continue
        area_geom = to_metric(shape(f["geometry"]))
        total = 0.0
        weight = 0.0
        for idx in tree.query(area_geom):
            tract_geom = tract_geoms[idx]
            if tract_areas[idx] <= 0 or tract_vals[idx] is None:
                continue
            inter = area_geom.intersection(tract_geom).area
            if inter <= 0:
                continue
            frac = inter / tract_areas[idx]
            if kind == "extensive":
                total += tract_vals[idx] * frac
            else:  # intensive: weight by the overlapping area
                total += tract_vals[idx] * inter
                weight += inter
        result = total if kind == "extensive" else (total / weight if weight else None)
        props = dict(f.get("properties") or {})
        props[out_field] = round(result, 4) if result is not None else None
        out.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return feature_collection(out)


def _num(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _combine(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    return feature_collection(features_of(a) + features_of(b))
