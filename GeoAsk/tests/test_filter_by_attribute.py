from __future__ import annotations

import pytest

from app.spatial import filter_by_attribute


def test_filter_greater_than(square_tracts):
    result = filter_by_attribute(square_tracts, "pct_senior", ">", 20.0)
    names = [f["properties"]["tract"] for f in result["features"]]
    assert names == ["east"]


def test_filter_equality_on_bool(two_pharmacies):
    result = filter_by_attribute(two_pharmacies, "open_24h", "==", True)
    names = [f["properties"]["name"] for f in result["features"]]
    assert names == ["A"]


def test_missing_attribute_drops_feature(square_tracts):
    result = filter_by_attribute(square_tracts, "nonexistent", ">", 0)
    assert result["features"] == []


def test_unknown_operator_raises(square_tracts):
    with pytest.raises(ValueError):
        filter_by_attribute(square_tracts, "population", "=>", 0)


def test_incomparable_types_raise(two_pharmacies):
    with pytest.raises(ValueError):
        filter_by_attribute(two_pharmacies, "name", ">", 5)
