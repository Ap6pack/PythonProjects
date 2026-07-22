from __future__ import annotations

from app.spatial import buffer, spatial_join


def test_matching_finds_tracts_intersecting_buffer(square_tracts, one_pharmacy):
    # A 1 km buffer around the west tract's corner only touches the west tract.
    zone = buffer(one_pharmacy, 1000.0)
    result = spatial_join(square_tracts, zone, predicate="intersects", keep="matching")
    names = [f["properties"]["tract"] for f in result["features"]]
    assert names == ["west"]


def test_non_matching_is_the_access_gap(square_tracts, one_pharmacy):
    zone = buffer(one_pharmacy, 1000.0)
    result = spatial_join(square_tracts, zone, predicate="intersects", keep="non_matching")
    names = [f["properties"]["tract"] for f in result["features"]]
    assert names == ["east"]


def test_match_count_is_attached(square_tracts, one_pharmacy):
    zone = buffer(one_pharmacy, 1000.0)
    result = spatial_join(square_tracts, zone, keep="matching")
    assert result["features"][0]["properties"]["_match_count"] == 1


def test_empty_join_yields_all_non_matching(square_tracts):
    empty = {"type": "FeatureCollection", "features": []}
    result = spatial_join(square_tracts, empty, keep="non_matching")
    assert len(result["features"]) == 2
