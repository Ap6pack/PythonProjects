# GeoAsk

A natural-language-to-map engine: ask a spatial question in plain English, get a
map back — no GIS knowledge required. Built open-first (PostGIS + open data),
with a clean path to ArcGIS deployment for clients who need the authoritative
version.

This repository contains the **engine**: the deterministic spatial primitives
(plan Phase 1), the dev-environment + PostGIS data layer (Phase 0), and the
**AI orchestration layer** (Phase 2) that turns a plain-English question into a
validated chain of primitive calls. The frontend (Phase 3) builds on top of this
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

## AI orchestration (`app/orchestration/`)

Phase 2 translates a plain-English question into a chain of primitive calls via
LLM function calling (Claude, `claude-opus-4-8`, adaptive thinking). The pipeline
is **parse → plan → execute → assemble**, and it holds the plan's load-bearing
rule: *the LLM never touches raw data.*

That rule is enforced structurally by a **layer store**. Every tool takes and
returns opaque layer handles (`layer_1`, `layer_2`, …) plus a geometry-free
summary (feature count, property names); the model chains steps by passing
handles. It never sees a coordinate, which keeps its context small and means a
malformed tool call can at worst name a handle that doesn't exist — which the
executor rejects and hands back for repair.

- **Tool schemas** (`tools.py`) mirror the primitives + two data-loading entry
  points, so the model can only ever request validated operations.
- **Guardrails**: the executor turns any primitive `ValueError` (bad distance,
  unknown operator, empty layer) into an `is_error` tool result the model
  corrects on its next turn — the request doesn't fail.
- **Transparency trace**: every tool call and its geometry-free result is
  recorded in order — the "what the AI did" panel, straight from the engine.
- **Injectable boundaries**: both the LLM (`LLMClient`) and the data source
  (`DataSource`) are protocols, so the whole loop is tested with a scripted fake
  model and an in-memory source — a full multi-step access-gap chain, error
  repair, bad-handle rejection, and the no-raw-geometry invariant, all with no
  API key or database (`tests/test_orchestration.py`).

Exposed as `POST /ask` (`{"question": "..."}` → `{geojson, explanation, trace}`);
it returns 503 rather than pretending if `ANTHROPIC_API_KEY` or `DATABASE_URL`
is unset.

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
- **Phase 1 — Spatial primitives:** ✅ implemented, tested, exposed via API; isochrone backed by a routing engine
- **Phase 2 — AI orchestration:** ✅ parse → plan → execute → assemble over the primitives, layer-handle isolation, guardrails, transparency trace, `POST /ask` (40 tests total, incl. a full scripted access-gap chain and live-PostGIS integration)
- **Phase 3 — Map & chat frontend:** next — MapLibre + chat + the transparency panel (render `geojson` + `trace` from `/ask`)
- **Phases 4–5 — MVP & pilot:** the access-gap finder, then real-user validation

The `demo_access_gap.py` trace is a preview of the transparency panel: it prints
exactly what the engine did at each step, which the plan calls non-negotiable
for trust.
