from __future__ import annotations

import pytest
from shapely.geometry import shape

from app.spatial import isochrone


def test_drive_is_larger_than_walk(one_pharmacy):
    drive = shape(isochrone(one_pharmacy, 10, mode="drive")["features"][0]["geometry"])
    walk = shape(isochrone(one_pharmacy, 10, mode="walk")["features"][0]["geometry"])
    assert drive.area > walk.area


def test_result_is_flagged_approximate(one_pharmacy):
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
