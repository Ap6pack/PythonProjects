"""Integration tests against a live PostGIS.

Skipped automatically unless ``DATABASE_URL`` points at a reachable PostGIS with
the postgis extension available. Run them with, e.g.:

    docker compose up -d db
    DATABASE_URL=postgresql://geoask:geoask@localhost:5432/geoask pytest -m postgis

They prove the whole data path: schema -> load -> query -> GeoJSON -> primitive.
"""

from __future__ import annotations

import os

import pytest

from app import data_access, spatial

psycopg = pytest.importorskip("psycopg")

pytestmark = pytest.mark.postgis


@pytest.fixture(scope="module")
def conn():
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set")
    try:
        connection = psycopg.connect(url)
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostGIS not reachable: {exc}")

    from app import db

    try:
        db.apply_schema(connection)
    except psycopg.errors.FeatureNotSupported:
        connection.close()
        pytest.skip("postgis extension not available on server")

    # Fresh sample data for the module.
    connection.execute("DELETE FROM pois; DELETE FROM tracts;")
    connection.execute(
        "INSERT INTO pois (category, name, geom) VALUES "
        "('pharmacy','Central', ST_SetSRID(ST_MakePoint(-122.68,45.52),4326))"
    )
    connection.execute(
        """
        INSERT INTO tracts (geoid, population, pct_senior, median_income, geom) VALUES
        ('near', 1000, 12.0, 60000, ST_Multi(ST_GeomFromText(
          'POLYGON((-122.685 45.515,-122.675 45.515,-122.675 45.525,-122.685 45.525,-122.685 45.515))',4326))),
        ('far', 1500, 28.0, 55000, ST_Multi(ST_GeomFromText(
          'POLYGON((-122.40 45.52,-122.39 45.52,-122.39 45.53,-122.40 45.53,-122.40 45.52))',4326)))
        """
    )
    connection.commit()
    yield connection
    connection.close()


def test_pois_by_category_returns_geojson(conn):
    fc = data_access.pois_by_category(conn, "pharmacy")
    assert len(fc["features"]) == 1
    assert fc["features"][0]["geometry"]["type"] == "Point"


def test_acceptance_query_only_returns_near_tract(conn):
    fc = data_access.tracts_within_of_category(conn, "pharmacy", 2000)
    assert [f["properties"]["geoid"] for f in fc["features"]] == ["near"]


def test_db_geojson_flows_into_primitive(conn):
    tracts = data_access.all_tracts(conn)
    seniors = spatial.filter_by_attribute(tracts, "pct_senior", ">", 20)
    assert [f["properties"]["geoid"] for f in seniors["features"]] == ["far"]
