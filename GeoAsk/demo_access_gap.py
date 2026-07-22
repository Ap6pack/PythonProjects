"""End-to-end access-gap demo — the MVP question type, run by hand.

Question: "Which neighbourhoods are more than a 10-minute drive from a pharmacy
and have an above-average senior population?"

This chains the primitives exactly the way the Phase 2 orchestration layer will,
and prints the transparency trace (the "what the AI did" panel) as it goes. It
uses small in-memory sample data so it runs with no database:

    python demo_access_gap.py
"""

from __future__ import annotations

from app.spatial import (
    demographic_overlay,
    filter_by_attribute,
    isochrone,
    spatial_join,
)

# --- sample pilot data (stands in for the PostGIS tables) --------------------
LON, LAT = -122.68, 45.52

PHARMACIES = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [LON, LAT]},
        "properties": {"name": "Central Pharmacy"},
    }],
}


def _tract(name, x0, y0, size, population, pct_senior):
    ring = [[x0, y0], [x0 + size, y0], [x0 + size, y0 + size], [x0, y0 + size], [x0, y0]]
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [ring]},
        "properties": {"tract": name, "population": population, "pct_senior": pct_senior},
    }


TRACTS = {
    "type": "FeatureCollection",
    "features": [
        _tract("near-young", LON - 0.01, LAT - 0.01, 0.02, 1500, 8.0),   # near pharmacy
        _tract("far-senior", LON + 0.20, LAT, 0.02, 1200, 27.0),         # far + senior
        _tract("far-young", LON + 0.20, LAT + 0.03, 0.02, 1800, 9.0),    # far + young
    ],
}

AVG_SENIOR = sum(f["properties"]["pct_senior"] for f in TRACTS["features"]) / len(TRACTS["features"])


def main() -> None:
    trace = []

    # 1. 10-minute drive-time reachable area around each pharmacy.
    zones = isochrone(PHARMACIES, minutes=10, mode="drive")
    trace.append("Built 10-minute drive-time areas around 1 pharmacy (approximate).")

    # 2. Tracts NOT reached by any drive-time area = the access gap.
    gap = spatial_join(TRACTS, zones, predicate="intersects", keep="non_matching")
    trace.append(f"Selected {len(gap['features'])} tracts outside every drive-time area.")

    # 3. Attach senior share to the gap tracts (already present; overlay would do
    #    this from raw ACS tracts in the real pipeline).
    gap = demographic_overlay(gap, TRACTS, "pct_senior", kind="intensive")
    trace.append("Overlaid senior-population share onto the gap tracts.")

    # 4. Keep only above-average-senior tracts.
    result = filter_by_attribute(gap, "pct_senior", ">", AVG_SENIOR)
    trace.append(f"Kept tracts with senior share above the {AVG_SENIOR:.1f}% average.")

    print("Question: neighbourhoods >10 min from a pharmacy with above-average seniors\n")
    print("What the engine did:")
    for i, step in enumerate(trace, 1):
        print(f"  {i}. {step}")
    print("\nAnswer — matching tracts:")
    for f in result["features"]:
        p = f["properties"]
        print(f"  - {p['tract']}: {p['pct_senior']:.0f}% senior")

    assert [f["properties"]["tract"] for f in result["features"]] == ["far-senior"], (
        "expected only 'far-senior' to match"
    )
    print("\n(sanity check passed)")


if __name__ == "__main__":
    main()
