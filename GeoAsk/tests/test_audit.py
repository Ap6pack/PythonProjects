"""Ground-truth baseline + audit harness tests — all offline (no model)."""

from __future__ import annotations

from app.orchestration.demo import _PLAN, _sample_source
from app.orchestration.llm import ScriptedClient
from evals.audit import ACCEPTANCE, render_report, run_audit, summarize
from evals.ground_truth import manual_access_gap


# --- the manual-GIS baseline ------------------------------------------------

def test_baseline_access_gap_is_all_far_tracts():
    gap = manual_access_gap(_sample_source(), seniors=False)
    assert gap == {"Pleasant Vly", "Powellhurst", "Centennial", "Hazelwood"}


def test_baseline_senior_filter_drops_the_young_far_tract():
    gap = manual_access_gap(_sample_source(), seniors=True)
    # Centennial is far but young (9% < mean) — excluded.
    assert gap == {"Pleasant Vly", "Powellhurst", "Hazelwood"}


# --- the audit harness ------------------------------------------------------

def test_audit_against_scripted_planner_scores_and_reports():
    # The demo planner always applies the senior filter, so it's right on the
    # senior phrasings and wrong on the plain-access-gap ones — the harness
    # should detect exactly that.
    outcomes = run_audit(ScriptedClient(_PLAN), _sample_source())
    summary = summarize(outcomes)

    assert summary["n"] == 15
    assert summary["invariant_rate"] == 1.0          # never leaks a reachable tract
    assert 0.0 < summary["accuracy"] < 1.0           # right on some, wrong on others
    assert summary["passes_acceptance"] is (summary["accuracy"] >= ACCEPTANCE)
    # Every failure is a plain-access-gap phrasing missing the young far tract.
    for _, note in summary["failures"]:
        assert "Centennial" in note


def test_report_renders_key_metrics():
    outcomes = run_audit(ScriptedClient(_PLAN), _sample_source())
    report = render_report(outcomes, summarize(outcomes))
    assert "# GeoAsk accuracy audit" in report
    assert "Correct maps" in report
    assert "Time-to-answer" in report
    assert "Where it breaks" in report


def test_summarize_handles_all_correct():
    # A planner matching the baseline on every query passes acceptance at 100%.
    outcomes = run_audit(ScriptedClient(_PLAN), _sample_source())
    for o in outcomes:
        o.correct = True
    summary = summarize(outcomes)
    assert summary["accuracy"] == 1.0
    assert summary["passes_acceptance"] is True
    assert summary["failures"] == []
