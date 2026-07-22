"""The top phrasings real users try for the one MVP question type, plus a
scorer. This is the Phase 4 "handle the top ~15 phrasings" corpus and the
Phase 5 accuracy-audit seed.

Each phrasing is a different way of asking the same access-gap question over the
demo sample data. ``expects_seniors`` marks the ones that also constrain on the
senior population. The scorer checks the *access-gap* invariant that matters —
the near (reachable) neighbourhoods must never appear in the answer — rather than
an exact tract set, so it's robust to the model's reasonable choices (threshold,
10 vs 15 minutes).
"""

from __future__ import annotations

from typing import Any

# Neighbourhoods in the demo sample, split by whether they are reachable.
NEAR_TRACTS = {"Sellwood", "Richmond", "Montavilla"}
FAR_TRACTS = {"Pleasant Vly", "Powellhurst", "Centennial", "Hazelwood"}
FAR_SENIOR_TRACTS = {"Pleasant Vly", "Powellhurst", "Hazelwood"}  # pct_senior > 15

PHRASINGS: list[dict[str, Any]] = [
    {"q": "Which neighbourhoods are more than a 10-minute drive from a pharmacy?", "expects_seniors": False},
    {"q": "Show me the pharmacy deserts.", "expects_seniors": False},
    {"q": "Where are the gaps in pharmacy access?", "expects_seniors": False},
    {"q": "Which tracts can't reach a pharmacy within a 10 minute drive?", "expects_seniors": False},
    {"q": "Map areas underserved by pharmacies.", "expects_seniors": False},
    {"q": "Which communities are far from any pharmacy?", "expects_seniors": False},
    {"q": "Show neighbourhoods with poor pharmacy access.", "expects_seniors": False},
    {"q": "Neighbourhoods more than 10 minutes from a pharmacy with above-average seniors.", "expects_seniors": True},
    {"q": "Where do seniors live far from a pharmacy?", "expects_seniors": True},
    {"q": "Find pharmacy access gaps in areas with lots of older residents.", "expects_seniors": True},
    {"q": "Which underserved neighbourhoods have a high senior population?", "expects_seniors": True},
    {"q": "Show me pharmacy deserts that also skew elderly.", "expects_seniors": True},
    {"q": "Older communities that can't easily get to a pharmacy.", "expects_seniors": True},
    {"q": "Access gaps for pharmacies, prioritising areas with many seniors.", "expects_seniors": True},
    {"q": "Where are seniors most cut off from pharmacies?", "expects_seniors": True},
]


def score(question_meta: dict[str, Any], result) -> tuple[bool, str]:
    """Return (passed, reason) for one phrasing's orchestrator result."""
    if not result.finished or not result.geojson:
        return False, "did not finish with a map"
    names = {f["properties"].get("tract") for f in result.geojson["features"]}

    leaked = names & NEAR_TRACTS
    if leaked:
        return False, f"included reachable tracts (not a gap): {sorted(leaked)}"
    if not names:
        return False, "empty answer"
    if not names <= FAR_TRACTS:
        return False, f"answer outside the known tract set: {sorted(names - FAR_TRACTS)}"
    if question_meta["expects_seniors"] and not (names & FAR_SENIOR_TRACTS):
        return False, "asked for seniors but returned no senior tracts"
    return True, f"ok: {sorted(names)}"
