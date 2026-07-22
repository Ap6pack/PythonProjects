"""Shared fixtures: small, hand-checkable GeoJSON in a real metro (Portland, OR).

Coordinates are near 45.52 N, 122.68 W so the metric projection behaves like a
real deployment. Values are chosen so expected answers can be reasoned about by
hand in the tests rather than copied from the implementation.
"""

from __future__ import annotations

import pytest

# A rough Portland-area anchor.
LON, LAT = -122.68, 45.52


def _point(lon, lat, **props):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": props,
    }


def _fc(*features):
    return {"type": "FeatureCollection", "features": list(features)}


@pytest.fixture
def two_pharmacies():
    # ~1.5 km apart east-west (0.019 deg lon ~ 1.48 km at this latitude).
    return _fc(
        _point(LON, LAT, name="A", open_24h=True),
        _point(LON + 0.019, LAT, name="B", open_24h=False),
    )


@pytest.fixture
def one_pharmacy():
    return _fc(_point(LON, LAT, name="A"))


@pytest.fixture
def square_tracts():
    """Two adjacent 0.02x0.02 deg square tracts, each carrying a population and a
    senior percentage."""
    def square(x0, y0, size, **props):
        ring = [
            [x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]
        ]
        return {
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": props,
        }

    return _fc(
        square(LON, LAT, 0.02, tract="west", population=1000, pct_senior=10.0),
        square(LON + 0.02, LAT, 0.02, tract="east", population=2000, pct_senior=30.0),
    )
