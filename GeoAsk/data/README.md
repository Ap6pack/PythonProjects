# Data pipeline (Phase 0)

Goal of this phase: one pilot metro loaded into PostGIS and indexed, so every
later phase has correct, real data to run against.

## Layers

| Layer | Source | Notes |
|---|---|---|
| POIs (pharmacies, schools, groceries…) | Overture Places / OSM | Filter to the pilot bbox; keep `category`, `name`, geometry |
| Census tracts + ACS | US Census TIGER + ACS 5-year | Population, age bands, income; join ACS tables to tract geometries |
| Building footprints (optional) | MS Building Footprints | For finer-grained population dasymetric later |

## Load steps

1. **Pick the pilot bbox.** One metro (the scaffold assumes Portland, OR). Small
   enough to iterate in seconds, real enough to be representative.
2. **Pull POIs** for the bbox and load into `pois(category, name, geom)`.
3. **Pull tracts + ACS** and load into `tracts(geoid, population, pct_senior,
   median_income, geom)`.
4. **Index:** `CREATE INDEX ON pois USING GIST (geom);` and the same on `tracts`.
5. **Verify** with the Phase 0 acceptance query below.

## Phase 0 acceptance query

> tracts within 2 km of any pharmacy

```sql
SELECT DISTINCT t.geoid
FROM tracts t
JOIN pois p
  ON ST_DWithin(t.geom::geography, p.geom::geography, 2000)
WHERE p.category = 'pharmacy';
```

If this returns the correct tracts for the pilot region, Phase 0 is done: there
is real, indexed spatial data to build the primitives against.

## Relationship to the primitives

The Phase 1 primitives currently operate on in-memory GeoJSON (see `app/spatial`)
so they are testable without a database. The PostGIS layer feeds them: a thin
data-access module will query these tables, hand GeoJSON FeatureCollections to
the same primitive functions, and return the result. The primitive logic does
not change when the data source becomes the database — only where the GeoJSON
comes from.
