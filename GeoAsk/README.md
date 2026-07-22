# GeoAsk

A natural-language-to-map engine: ask a spatial question in plain English, get a
map back — no GIS knowledge required. Built open-first (PostGIS + open data),
with a clean path to ArcGIS deployment for clients who need the authoritative
version.

This repository currently contains the **foundation**: the deterministic spatial
primitives engine (plan Phase 1) and the dev-environment scaffolding (Phase 0).
The AI orchestration layer (Phase 2) and frontend (Phase 3) build on top of this
without changing it.

## Why this shape

The design rule from the project plan is load-bearing: **the LLM never touches
raw data.** It only calls a fixed set of validated spatial *tools*. So those
tools are built first — deterministic, independently tested, correct in metres —
before any model is involved. A plausible-but-wrong map is worse than no map, and
this is how you prevent one.

## The primitives (`app/spatial/`)

Each is a pure function over GeoJSON, so it is testable with no database.

| Primitive | What it does |
|---|---|
| `buffer` | Grow features by a distance in metres |
| `isochrone` | Road-network reachable area within a travel-time budget (routing engine; see below) |
| `filter_by_attribute` | Keep features whose property passes a comparison |
| `spatial_join` | Relate two layers by `intersects` / `within` / `contains`; `keep="non_matching"` gives you the access gap |
| `nearest` | For each source feature, the closest destination and its distance |
| `demographic_overlay` | Area-weighted aggregation of tract values (population, % senior) onto arbitrary areas |

All metric operations reproject to a local azimuthal-equidistant projection
centred on the working data, so distances and areas are correct — never computed
in raw degrees.

### On `isochrone`

The isochrone uses a **road-network routing engine** (Valhalla by default; see
`app/spatial/routing.py`). Point `VALHALLA_URL` at a Valhalla server and results
are true network isochrones, flagged `_isochrone_approx: false`. The routing
backend sits behind a small `RoutingClient` protocol, so it is swappable and
mockable in tests without a live server.

When no engine is configured, the primitive falls back to a straight-line buffer
at a mode-typical speed and flags the result `_isochrone_approx: true` — an
explicit, labelled fallback that keeps the no-infrastructure demo and tests
running, never a silent stand-in. The transparency panel uses the flag to tell
the user which backend produced the map.

## Run it

```bash
pip install -r requirements.txt

# tests — proves each primitive against known-correct outputs
pytest

# the end-to-end access-gap demo (the MVP question type), no DB needed
python demo_access_gap.py

# the API
uvicorn app.main:app --reload   # docs at http://localhost:8000/docs
```

Or the full Phase-0 environment (API + PostGIS):

```bash
docker compose up
```

## The API (`app/`)

Each primitive is exposed as a typed FastAPI endpoint under `/tools/*`
(`/tools/buffer`, `/tools/spatial_join`, …). These are the exact endpoints the
Phase 2 orchestration layer will drive via LLM function calling — the tool
schemas will mirror these request models. Malformed calls are rejected with a
422 before any geometry runs, which is the first of the plan's validation
guardrails.

## Data (`app/db.py`, `app/data_access.py`, `data/`, `sql/`)

The PostGIS data layer is built: `sql/schema.sql` defines the indexed `pois` and
`tracts` tables, `app/db.py` manages the connection and applies the schema, and
`app/data_access.py` turns rows into GeoJSON FeatureCollections (via
`ST_AsGeoJSON`) that feed the *same* tested primitives — the primitive logic is
identical whether the GeoJSON comes from memory or the database.

```bash
# bring up PostGIS, load a pilot region, and it's queryable
docker compose up -d db
DATABASE_URL=postgresql://geoask:geoask@localhost:5432/geoask \
  python -m data.load --pois pois.geojson --tracts tracts.geojson
```

`app/data_access.py` also implements the Phase 0 acceptance query (tracts within
2 km of a POI category) as `tracts_within_of_category`. The whole path —
schema → load → query → GeoJSON → primitive — is covered by integration tests
(`tests/test_postgis_integration.py`), which run against a live PostGIS and skip
cleanly when `DATABASE_URL` is unset. `data/README.md` documents the upstream
fetch of Overture/OSM POIs and Census/ACS tracts for a pilot bbox.

## Where this sits in the plan

- **Phase 0 — Foundation:** ✅ PostGIS schema + data-access layer + loader, Docker compose, verified acceptance query
- **Phase 1 — Spatial primitives:** ✅ implemented, tested (35 tests incl. live-PostGIS integration), exposed via API; isochrone backed by a routing engine
- **Phase 2 — AI orchestration:** next — tool schemas over these endpoints, parse → plan → execute → assemble
- **Phase 3 — Map & chat frontend:** MapLibre + chat + the transparency panel
- **Phases 4–5 — MVP & pilot:** the access-gap finder, then real-user validation

The `demo_access_gap.py` trace is a preview of the transparency panel: it prints
exactly what the engine did at each step, which the plan calls non-negotiable
for trust.
