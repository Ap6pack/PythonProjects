"""Scorer unit tests (run in CI) + the live phrasing eval (skips without a key)."""

from __future__ import annotations

import os

import pytest

from app.orchestration.orchestrator import AskResult
from evals.phrasings import PHRASINGS, score


def _result(tract_names):
    fc = {"type": "FeatureCollection",
          "features": [{"properties": {"tract": n}} for n in tract_names]}
    return AskResult(geojson=fc, explanation="", finished=True)


def test_corpus_is_fifteen_phrasings():
    assert len(PHRASINGS) == 15


def test_score_rejects_reachable_tract_leak():
    ok, reason = score({"expects_seniors": False}, _result(["Pleasant Vly", "Richmond"]))
    assert not ok and "reachable" in reason


def test_score_accepts_valid_gap():
    ok, _ = score({"expects_seniors": False}, _result(["Pleasant Vly", "Hazelwood"]))
    assert ok


def test_score_requires_seniors_when_asked():
    # Centennial is a far tract but young (not a senior tract).
    ok, reason = score({"expects_seniors": True}, _result(["Centennial"]))
    assert not ok and "senior" in reason


def test_score_rejects_unfinished():
    ok, _ = score({"expects_seniors": False}, AskResult(geojson=None, explanation="n/a", finished=False))
    assert not ok


@pytest.mark.skipif(
    not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")),
    reason="live LLM eval needs ANTHROPIC_API_KEY",
)
def test_live_phrasing_eval():
    """Full corpus against the real model over the in-memory sample. Target: all
    top phrasings resolve to a correct access-gap map without hand-holding."""
    from app.orchestration import ask
    from app.orchestration.demo import _sample_source
    from app.orchestration.llm import default_client

    source = _sample_source()
    client = default_client()
    failures = []
    for meta in PHRASINGS:
        ok, reason = score(meta, ask(meta["q"], client, source))
        if not ok:
            failures.append(f"{meta['q']} -> {reason}")
    assert not failures, "phrasings failed:\n" + "\n".join(failures)
