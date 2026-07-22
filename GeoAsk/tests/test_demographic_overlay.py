from __future__ import annotations

import pytest

from app.spatial import demographic_overlay


def _area_over_west_half(lon, lat):
    """A rectangle covering exactly the left (west) half of the west tract:
    x in [lon, lon+0.01], y in [lat, lat+0.02]. That is half of the west tract
    and none of the east tract."""
    ring = [
        [lon, lat], [lon + 0.01, lat], [lon + 0.01, lat + 0.02],
        [lon, lat + 0.02], [lon, lat],
    ]
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {"zone": "test"},
        }],
    }


def test_extensive_apportions_population_by_area(square_tracts):
    from tests.conftest import LON, LAT
    areas = _area_over_west_half(LON, LAT)
    result = demographic_overlay(areas, square_tracts, "population", kind="extensive")
    # Half of the west tract's 1000 people, none of the east tract.
    assert result["features"][0]["properties"]["population"] == pytest.approx(500, rel=0.02)


def test_intensive_is_area_weighted_mean(square_tracts):
    from tests.conftest import LON, LAT
    # Area covering both full tracts -> weighted mean of 10% (west) and 30%
    # (east), weighted equally since tracts are equal area -> 20%.
    ring = [
        [LON, LAT], [LON + 0.04, LAT], [LON + 0.04, LAT + 0.02],
        [LON, LAT + 0.02], [LON, LAT],
    ]
    areas = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {},
        }],
    }
    result = demographic_overlay(areas, square_tracts, "pct_senior", kind="intensive")
    assert result["features"][0]["properties"]["pct_senior"] == pytest.approx(20.0, rel=0.02)


def test_empty_tracts_raises(square_tracts):
    empty = {"type": "FeatureCollection", "features": []}
    with pytest.raises(ValueError):
        demographic_overlay(square_tracts, empty, "population")
