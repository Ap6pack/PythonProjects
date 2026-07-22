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
| `isochrone` | Reachable area within a travel-time budget (**approximate** — see below) |
| `filter_by_attribute` | Keep features whose property passes a comparison |
| `spatial_join` | Relate two layers by `intersects` / `within` / `contains`; `keep="non_matching"` gives you the access gap |
| `nearest` | For each source feature, the closest destination and its distance |
| `demographic_overlay` | Area-weighted aggregation of tract values (population, % senior) onto arbitrary areas |

All metric operations reproject to a local azimuthal-equidistant projection
centred on the working data, so distances and areas are correct — never computed
in raw degrees.

### On `isochrone`

The isochrone is currently a documented **approximation**: a straight-line
buffer at a mode-typical speed with a detour discount. A true isochrone follows
the road network and needs a routing engine (OSRM / Valhalla / pgRouting). The
function already has the final signature (`minutes`, `mode`), so swapping in the
routing engine is an internal change no caller sees. Results are flagged
`_isochrone_approx: true` so the transparency panel can label them honestly.

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

## Data (`data/`)

`data/README.md` describes the Phase 0 pipeline: load one pilot metro's POIs and
Census tracts into PostGIS, index them, and verify with a known spatial query.
The primitives are written to consume GeoJSON from that database unchanged — the
data source becomes PostGIS without the primitive logic changing.

## Where this sits in the plan

- **Phase 0 — Foundation:** ✅ scaffolded (Docker + PostGIS compose, data pipeline doc)
- **Phase 1 — Spatial primitives:** ✅ implemented, tested (26 tests), exposed via API
- **Phase 2 — AI orchestration:** next — tool schemas over these endpoints, parse → plan → execute → assemble
- **Phase 3 — Map & chat frontend:** MapLibre + chat + the transparency panel
- **Phases 4–5 — MVP & pilot:** the access-gap finder, then real-user validation

The `demo_access_gap.py` trace is a preview of the transparency panel: it prints
exactly what the engine did at each step, which the plan calls non-negotiable
for trust.
