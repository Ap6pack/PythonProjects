"""Unit tests for the row -> GeoJSON assembly, with no database.

These exercise the mapping logic against a fake cursor so the FeatureCollection
shape is verified even where PostGIS is not installed. The live-database path is
covered separately in test_postgis_integration.py.
"""

from __future__ import annotations

from app import data_access


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params):
        self.sql, self.params = sql, params

    def fetchall(self):
        return self._rows


class FakeConn:
    def __init__(self, rows):
        self._rows = rows
        self.cursor_obj = None

    def cursor(self):
        self.cursor_obj = FakeCursor(self._rows)
        return self.cursor_obj


def test_pois_by_category_builds_features():
    rows = [('{"type":"Point","coordinates":[-122.68,45.52]}', "pharmacy", "Central")]
    conn = FakeConn(rows)
    fc = data_access.pois_by_category(conn, "pharmacy")

    assert fc["type"] == "FeatureCollection"
    feat = fc["features"][0]
    assert feat["geometry"] == {"type": "Point", "coordinates": [-122.68, 45.52]}
    assert feat["properties"] == {"category": "pharmacy", "name": "Central"}
    # The category filter is passed as a bound parameter, not interpolated.
    assert conn.cursor_obj.params == ("pharmacy",)


def test_tracts_within_passes_both_params():
    conn = FakeConn([])
    data_access.tracts_within_of_category(conn, "pharmacy", 2000)
    assert conn.cursor_obj.params == ("pharmacy", 2000)


def test_all_tracts_maps_property_columns():
    rows = [(
        '{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,0]]]}',
        "near", 1000, 12.0, 60000,
    )]
    fc = data_access.all_tracts(FakeConn(rows))
    props = fc["features"][0]["properties"]
    assert props == {
        "geoid": "near", "population": 1000, "pct_senior": 12.0, "median_income": 60000,
    }
