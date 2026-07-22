from __future__ import annotations

import math

import pytest
from shapely.geometry import shape

from app.spatial import buffer


def test_buffer_produces_polygon_of_expected_radius(one_pharmacy):
    result = buffer(one_pharmacy, 500.0)
    assert len(result["features"]) == 1
    geom = shape(result["features"][0]["geometry"])
    assert geom.geom_type == "Polygon"

    # The buffered point should reach ~500 m from the origin. Check the polygon's
    # bounding half-width in metres via a quick equirectangular approximation.
    minx, miny, maxx, maxy = geom.bounds
    lat = one_pharmacy["features"][0]["geometry"]["coordinates"][1]
    half_width_m = (maxx - minx) / 2 * 111_320 * math.cos(math.radians(lat))
    assert half_width_m == pytest.approx(500, rel=0.02)


def test_buffer_preserves_properties(one_pharmacy):
    result = buffer(one_pharmacy, 100.0)
    assert result["features"][0]["properties"]["name"] == "A"


def test_buffer_rejects_nonpositive_distance(one_pharmacy):
    with pytest.raises(ValueError):
        buffer(one_pharmacy, 0)
