from __future__ import annotations

import pytest

from app.spatial import nearest


def test_nearest_distance_and_attributes(one_pharmacy, two_pharmacies):
    # Source is a single point coincident with pharmacy A; nearest of the two
    # pharmacies is A at ~0 m.
    result = nearest(one_pharmacy, two_pharmacies)
    props = result["features"][0]["properties"]
    assert props["_nearest_distance_m"] == pytest.approx(0, abs=1)
    assert props["nearest_name"] == "A"


def test_nearest_picks_closer_of_two(two_pharmacies, one_pharmacy):
    # From the two pharmacies, the nearest single destination (A) is A for A
    # (0 m) and ~1.48 km for B.
    result = nearest(two_pharmacies, one_pharmacy)
    dists = [f["properties"]["_nearest_distance_m"] for f in result["features"]]
    assert dists[0] == pytest.approx(0, abs=1)
    assert dists[1] == pytest.approx(1480, rel=0.05)


def test_empty_destinations_raises(one_pharmacy):
    empty = {"type": "FeatureCollection", "features": []}
    with pytest.raises(ValueError):
        nearest(one_pharmacy, empty)
