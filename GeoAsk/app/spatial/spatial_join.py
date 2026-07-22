"""spatial_join — relate two collections by a topological predicate.

Two modes, both common in access-gap work:

* ``keep="matching"`` — return the target features that satisfy the predicate
  against *any* join feature (e.g. "tracts that intersect a drive-time area").
* ``keep="non_matching"`` — the inverse (e.g. "tracts *outside* every drive-time
  area"), which is the access-gap itself.

Each returned target gets a ``_match_count`` property so downstream steps can
filter on it. Predicates are pure topology (no distance), so this runs in the
native WGS84 coordinates without reprojection.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import shape
from shapely.strtree import STRtree

from .geo import feature_collection, features_of

_PREDICATES = {"intersects", "within", "contains"}


def spatial_join(
    target: dict[str, Any],
    join: dict[str, Any],
    predicate: str = "intersects",
    keep: str = "matching",
) -> dict[str, Any]:
    if predicate not in _PREDICATES:
        raise ValueError(f"unknown predicate {predicate!r}; expected {sorted(_PREDICATES)}")
    if keep not in {"matching", "non_matching"}:
        raise ValueError("keep must be 'matching' or 'non_matching'")

    target_features = features_of(target)
    join_features = [f for f in features_of(join) if f.get("geometry")]
    join_geoms = [shape(f["geometry"]) for f in join_features]

    # STRtree gives us a candidate shortlist per target; we still confirm the
    # exact predicate because the tree only tests bounding boxes.
    tree = STRtree(join_geoms) if join_geoms else None

    out = []
    for f in target_features:
        if not f.get("geometry"):
            continue
        geom = shape(f["geometry"])
        count = 0
        if tree is not None:
            for idx in tree.query(geom):
                other = join_geoms[idx]
                if _test(geom, other, predicate):
                    count += 1
        matched = count > 0
        if matched == (keep == "matching"):
            props = dict(f.get("properties") or {})
            props["_match_count"] = count
            out.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
    return feature_collection(out)


def _test(a, b, predicate: str) -> bool:
    if predicate == "intersects":
        return a.intersects(b)
    if predicate == "within":
        return a.within(b)
    return a.contains(b)  # "contains"
