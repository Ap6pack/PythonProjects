"""Load GeoJSON POIs and tracts into PostGIS (Phase 0 pipeline entry point).

This is intentionally minimal: it applies the schema and bulk-loads two GeoJSON
files into the ``pois`` and ``tracts`` tables. The heavy lifting of *fetching*
Overture/OSM POIs and Census/ACS tracts for a pilot bbox is upstream of this
(see data/README.md); this step is the "load and index" half, and it is what the
integration tests and demo run against.

    DATABASE_URL=... python -m data.load --pois pois.geojson --tracts tracts.geojson
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app import db


def _load_pois(conn, path: Path) -> int:
    fc = json.loads(path.read_text())
    n = 0
    for f in fc.get("features", []):
        props = f.get("properties") or {}
        conn.execute(
            "INSERT INTO pois (category, name, geom) "
            "VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))",
            (props.get("category"), props.get("name"), json.dumps(f["geometry"])),
        )
        n += 1
    return n


def _load_tracts(conn, path: Path) -> int:
    fc = json.loads(path.read_text())
    n = 0
    for f in fc.get("features", []):
        props = f.get("properties") or {}
        conn.execute(
            "INSERT INTO tracts (geoid, population, pct_senior, median_income, geom) "
            "VALUES (%s, %s, %s, %s, ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))) "
            "ON CONFLICT (geoid) DO NOTHING",
            (
                props.get("geoid"),
                props.get("population"),
                props.get("pct_senior"),
                props.get("median_income"),
                json.dumps(f["geometry"]),
            ),
        )
        n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser(description="Load pilot-region data into PostGIS")
    parser.add_argument("--pois", type=Path, help="GeoJSON of POI points")
    parser.add_argument("--tracts", type=Path, help="GeoJSON of tract polygons")
    args = parser.parse_args()

    with db.connect() as conn:
        db.apply_schema(conn)
        if args.pois:
            print(f"loaded {_load_pois(conn, args.pois)} POIs")
        if args.tracts:
            print(f"loaded {_load_tracts(conn, args.tracts)} tracts")
        conn.commit()


if __name__ == "__main__":
    main()
