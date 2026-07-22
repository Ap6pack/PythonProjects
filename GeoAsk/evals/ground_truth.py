"""The "manual GIS" baseline — deterministic reference answers.

Phase 5's accuracy audit spot-checks the AI's maps against manual GIS analysis.
This module *is* that manual analysis, encoded: it chains the tested primitives
the way a competent analyst would, with no LLM, to compute the known-correct
answer for each question type. The audit then measures how often the AI's plan
reproduces this reference.

Computing the baseline from the same validated primitives the AI orchestrates is
the point: the primitives are the ground-truth spatial operations (Phase 1,
tested against known outputs); what's under test in the pilot is whether the
model *plans the right chain*, not whether the operations are correct.
"""

from __future__ import annotations

from app.spatial import filter_by_attribute, isochrone, spatial_join
from app.spatial.geo import features_of


def _mean_pct_senior(tracts: dict) -> float:
    vals = [f["properties"]["pct_senior"] for f in features_of(tracts)
            if f.get("properties", {}).get("pct_senior") is not None]
    return sum(vals) / len(vals) if vals else 0.0


def manual_access_gap(
    source,
    *,
    seniors: bool,
    minutes: float = 10,
    mode: str = "drive",
) -> set[str]:
    """The reference set of tract names for an access-gap question.

    ``seniors=True`` additionally keeps only tracts whose senior share is above
    the mean across all tracts — the natural reading of "above-average seniors".
    """
    pharmacies = source.load_pois("pharmacy")
    areas = isochrone(pharmacies, minutes, mode)
    tracts = source.load_tracts()
    gap = spatial_join(tracts, areas, "intersects", "non_matching")
    if seniors:
        threshold = _mean_pct_senior(tracts)
        gap = filter_by_attribute(gap, "pct_senior", ">", threshold)
    return {f["properties"].get("tract") for f in features_of(gap)}
