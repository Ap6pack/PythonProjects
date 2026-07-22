# Validation & accuracy audit (Phase 5)

Phase 5 asks: does GeoAsk work for someone who isn't you? The acceptance bar is
**≥80% of realistic user questions return a correct, useful map**, with a
documented comparison against manual GIS analysis. This directory is the harness
that measures it.

## The pieces

| File | What it is |
|---|---|
| `phrasings.py` | 15 real phrasings of the one MVP question (access-gap), + a scorer for the access-gap invariant |
| `ground_truth.py` | The **manual-GIS baseline** — the known-correct answer per question, computed deterministically from the tested primitives (no LLM) |
| `audit.py` | Runs the corpus through the model, times each query, compares to the baseline, reports success rate + time-to-answer + where it breaks |
| `run.py` | Lighter pass/fail runner over the invariant scorer |

## How accuracy is measured

The audit compares two things over the same sample data:

1. **Manual baseline** (`ground_truth.manual_access_gap`) — an analyst's correct
   chain, encoded: isochrone → spatial-join (keep non-matching) → optional
   above-average-senior filter. Deterministic, LLM-free. This is the "manual GIS
   analysis" the plan says to spot-check against.
2. **The AI's answer** — what the orchestrator's plan actually produced.

A query is **correct** when the AI's tract set exactly matches the baseline. A
looser **invariant** check (a *reachable* neighbourhood must never appear in an
access-gap answer) catches the failure that would most mislead a user, and is
robust to defensible modelling choices (10 vs 12 minutes, threshold).

`time-to-answer` is measured per query so the pilot can compare it against the
manual workflow (minutes-to-hours in a desktop GIS).

## Running it

```bash
# Audit the live model (the pilot run)
ANTHROPIC_API_KEY=... python -m evals.audit

# Offline: print the manual-GIS reference answers the pilot audits against
python -m evals.audit
```

`audit.py` exits non-zero if accuracy is below the 80% bar, so it can gate a
release.

## Manual-GIS reference answers (sample data)

Generated offline from `ground_truth.py` over the demo sample (2 pharmacies,
7 tracts). These are the correct maps; the audit measures how often the model
reproduces them.

| Question type | Correct answer |
|---|---|
| Access gap, no demographic filter | Centennial, Hazelwood, Pleasant Vly, Powellhurst |
| Access gap, above-average seniors | Hazelwood, Pleasant Vly, Powellhurst |

## What's automated vs. what needs the pilot

The harness — baseline, scoring, timing, report, acceptance gate — is code and is
unit-tested in CI. What it can't manufacture is the pilot itself: a live model
(API key), real POI/Census data for the region, and 2–3 real gov/planning users
asking their own questions. Point the harness at those and it produces the
Phase 5 scorecard.
