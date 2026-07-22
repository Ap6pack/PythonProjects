"""isochrone — reachable area within a travel-time budget.

Reachability follows the road network via a routing engine (Valhalla by
default; see ``routing.py``). When a routing engine is configured, results are
true network isochrones and are flagged ``_isochrone_approx: false``.

When no engine is configured, the primitive falls back to a straight-line buffer
at a mode-typical speed, discounted for detour, and flags the result
``_isochrone_approx: true``. The fallback keeps the no-infrastructure demo and
tests working, but it is always labelled so the transparency panel can tell the
user which one produced the map — a plausible-but-wrong reachability map is
exactly the failure mode the plan warns against.

Either way the signature is the same, so callers are unaffected by which backend
runs.
"""

from __future__ import annotations

from typing import Any

from shapely.geometry import shape

from .buffer import buffer
from .geo import feature, feature_collection, features_of
from .routing import RoutingClient, RoutingError, default_client

# Fallback speeds (km/h) and detour factor: the fraction of the straight-line
# radius actually reachable on real streets. Conservative on purpose.
_MODE_SPEED_KMH = {"walk": 5.0, "bike": 15.0, "drive": 40.0}
_DETOUR_FACTOR = 0.75


def isochrone(
    fc: dict[str, Any],
    minutes: float,
    mode: str = "drive",
    router: RoutingClient | None = None,
) -> dict[str, Any]:
    if mode not in _MODE_SPEED_KMH:
        raise ValueError(f"unknown mode {mode!r}; expected {sorted(_MODE_SPEED_KMH)}")
    if minutes <= 0:
        raise ValueError("minutes must be positive")

    # An explicitly passed router wins; otherwise fall back to env config.
    router = router or default_client()
    if router is not None:
        return _network_isochrone(fc, minutes, mode, router)
    return _approx_isochrone(fc, minutes, mode)


def _network_isochrone(
    fc: dict[str, Any], minutes: float, mode: str, router: RoutingClient
) -> dict[str, Any]:
    out = []
    for f in features_of(fc):
        geom = f.get("geometry")
        if not geom:
            continue
        # Origins are points; use a representative point for anything else.
        pt = shape(geom).representative_point()
        try:
            reachable = router.isochrone(pt.x, pt.y, minutes, mode)
        except RoutingError:
            # A single unreachable origin should not fail the whole request;
            # fall back to the approximation for that feature, clearly labelled.
            approx = _approx_isochrone(feature_collection([f]), minutes, mode)
            out.extend(approx["features"])
            continue
        props = dict(f.get("properties") or {})
        props.update(_isochrone_props(minutes, mode, approx=False))
        out.append(feature(shape(reachable), props))
    return feature_collection(out)


def _approx_isochrone(fc: dict[str, Any], minutes: float, mode: str) -> dict[str, Any]:
    radius_m = _MODE_SPEED_KMH[mode] * 1000.0 / 60.0 * minutes * _DETOUR_FACTOR
    result = buffer(fc, radius_m)
    for f in result["features"]:
        f["properties"].update(_isochrone_props(minutes, mode, approx=True))
    return result


def _isochrone_props(minutes: float, mode: str, approx: bool) -> dict[str, Any]:
    return {
        "_isochrone_minutes": minutes,
        "_isochrone_mode": mode,
        "_isochrone_approx": approx,
    }
