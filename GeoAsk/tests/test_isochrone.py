from __future__ import annotations

import pytest
from shapely.geometry import shape

from app.spatial import isochrone
from app.spatial.routing import RoutingError


class FakeRouter:
    """A stand-in routing engine returning a fixed square around the origin."""

    def __init__(self, half_deg=0.05):
        self.half = half_deg
        self.calls = []

    def isochrone(self, lon, lat, minutes, mode):
        self.calls.append((lon, lat, minutes, mode))
        h = self.half
        ring = [
            [lon - h, lat - h], [lon + h, lat - h], [lon + h, lat + h],
            [lon - h, lat + h], [lon - h, lat - h],
        ]
        return {"type": "Polygon", "coordinates": [ring]}


class BrokenRouter:
    def isochrone(self, lon, lat, minutes, mode):
        raise RoutingError("engine down")


# --- real routing path -------------------------------------------------------

def test_uses_router_when_provided(one_pharmacy):
    router = FakeRouter()
    result = isochrone(one_pharmacy, 10, mode="drive", router=router)
    props = result["features"][0]["properties"]
    assert props["_isochrone_approx"] is False
    assert router.calls == [(-122.68, 45.52, 10, "drive")]


def test_router_geometry_is_returned(one_pharmacy):
    router = FakeRouter(half_deg=0.05)
    geom = shape(isochrone(one_pharmacy, 10, router=router)["features"][0]["geometry"])
    # The fake returns a 0.1-deg square; its bounds should reflect that, not a
    # circular buffer.
    minx, miny, maxx, maxy = geom.bounds
    assert (maxx - minx) == pytest.approx(0.1, abs=1e-6)


def test_router_failure_falls_back_labelled(one_pharmacy):
    result = isochrone(one_pharmacy, 10, mode="drive", router=BrokenRouter())
    props = result["features"][0]["properties"]
    # Fell back to the approximation, and said so.
    assert props["_isochrone_approx"] is True


# --- approximation fallback --------------------------------------------------

def test_fallback_drive_is_larger_than_walk(one_pharmacy):
    drive = shape(isochrone(one_pharmacy, 10, mode="drive")["features"][0]["geometry"])
    walk = shape(isochrone(one_pharmacy, 10, mode="walk")["features"][0]["geometry"])
    assert drive.area > walk.area


def test_fallback_is_flagged_approximate(one_pharmacy):
    props = isochrone(one_pharmacy, 10, mode="drive")["features"][0]["properties"]
    assert props["_isochrone_approx"] is True
    assert props["_isochrone_minutes"] == 10
    assert props["_isochrone_mode"] == "drive"


def test_unknown_mode_raises(one_pharmacy):
    with pytest.raises(ValueError):
        isochrone(one_pharmacy, 10, mode="teleport")


def test_nonpositive_minutes_raises(one_pharmacy):
    with pytest.raises(ValueError):
        isochrone(one_pharmacy, 0, mode="drive")
