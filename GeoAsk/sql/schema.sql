-- GeoAsk PostGIS schema (Phase 0).
-- One pilot region's POIs and Census tracts, indexed for spatial queries.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS pois (
    id       BIGSERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    name     TEXT,
    geom     geometry(Point, 4326) NOT NULL
);

CREATE TABLE IF NOT EXISTS tracts (
    geoid         TEXT PRIMARY KEY,
    population    INTEGER,
    pct_senior    DOUBLE PRECISION,
    median_income INTEGER,
    geom          geometry(MultiPolygon, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS pois_geom_gix   ON pois  USING GIST (geom);
CREATE INDEX IF NOT EXISTS pois_category_ix ON pois (category);
CREATE INDEX IF NOT EXISTS tracts_geom_gix ON tracts USING GIST (geom);
