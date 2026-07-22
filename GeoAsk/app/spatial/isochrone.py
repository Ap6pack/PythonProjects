"""isochrone — reachable area within a travel-time budget.

MVP status: this is the *approximate* implementation. A true isochrone follows
the road network and needs a routing engine (OSRM, Valhalla, or pgRouting over
the OSM graph). Until that engine is wired in, we approximate the reachable area
as a straight-line buffer at a mode-typical speed, discounted by a detour factor
that accounts for real streets rarely running straight to the destination.

This is deliberately a thin wrapper over ``buffer`` with the *exact signature*
the real isochrone will have (``mode``, ``minutes``), so swapping in the routing
engine later is an internal change no caller sees. The transparency panel must
label results from this path as approximate — a plausible-but-wrong reachability
map is exactly the failure mode the plan calls out.
"""

from __future__ import annotations

from typing import Any

from .buffer import buffer

# Typical door-to-door speeds (km/h) and a detour factor: the fraction of the
# straight-line radius actually reachable once you follow streets. Conservative
# on purpose — better to under-claim reach than over-claim it.
_MODE_SPEED_KMH = {"walk": 5.0, "bike": 15.0, "drive": 40.0}
_DETOUR_FACTOR = 0.75


def isochrone(fc: dict[str, Any], minutes: float, mode: str = "drive") -> dict[str, Any]:
    if mode not in _MODE_SPEED_KMH:
        raise ValueError(f"unknown mode {mode!r}; expected {sorted(_MODE_SPEED_KMH)}")
    if minutes <= 0:
        raise ValueError("minutes must be positive")

    speed_kmh = _MODE_SPEED_KMH[mode]
    radius_m = speed_kmh * 1000.0 / 60.0 * minutes * _DETOUR_FACTOR

    result = buffer(fc, radius_m)
    for f in result["features"]:
        f["properties"]["_isochrone_minutes"] = minutes
        f["properties"]["_isochrone_mode"] = mode
        f["properties"]["_isochrone_approx"] = True
    return result
