"""Accuracy audit + measurement harness for the pilot (Phase 5).

Runs the phrasing corpus through an orchestrator, times each query, compares the
AI's answer to the deterministic manual-GIS baseline (``ground_truth``), and
reports the metrics the plan calls for: query success rate, time-to-answer, and
where it breaks. The plan's acceptance bar is ≥80% correct maps.

    ANTHROPIC_API_KEY=... python -m evals.audit      # audit the live model
    python -m evals.audit                            # offline: print the
                                                     # manual-baseline reference

The scoring and report functions are pure so they're unit-tested without a model
(``tests/test_audit.py``); the live audit is the pilot run.
"""

from __future__ import annotations

import statistics
import sys
import time
from dataclasses import dataclass

from app.orchestration import ask
from app.orchestration.demo import _sample_source
from app.orchestration.llm import LLMClient, default_client

from .ground_truth import manual_access_gap
from .phrasings import PHRASINGS, score

ACCEPTANCE = 0.80  # ≥80% of realistic questions return a correct, useful map


@dataclass
class QueryOutcome:
    question: str
    expected: set[str]
    actual: set[str] | None
    correct: bool          # exact match against the manual baseline
    invariant_ok: bool     # the access-gap invariant held (looser)
    seconds: float
    note: str


def reference_table(source) -> list[tuple[str, set[str]]]:
    """The manual-GIS reference answer for every phrasing — generatable with no
    model, this is the documented baseline the pilot audits against."""
    return [(m["q"], manual_access_gap(source, seniors=m["expects_seniors"])) for m in PHRASINGS]


def run_audit(client: LLMClient, source) -> list[QueryOutcome]:
    outcomes = []
    for m in PHRASINGS:
        expected = manual_access_gap(source, seniors=m["expects_seniors"])
        t0 = time.perf_counter()
        result = ask(m["q"], client, source)
        seconds = time.perf_counter() - t0
        actual = (
            {f["properties"].get("tract") for f in result.geojson["features"]}
            if result.geojson else None
        )
        ok, note = score(m, result)
        outcomes.append(QueryOutcome(m["q"], expected, actual, actual == expected, ok, seconds, note))
    return outcomes


def summarize(outcomes: list[QueryOutcome]) -> dict:
    n = len(outcomes)
    times = [o.seconds for o in outcomes]
    correct = sum(o.correct for o in outcomes)
    return {
        "n": n,
        "accuracy": correct / n if n else 0.0,
        "invariant_rate": sum(o.invariant_ok for o in outcomes) / n if n else 0.0,
        "mean_seconds": statistics.mean(times) if times else 0.0,
        "median_seconds": statistics.median(times) if times else 0.0,
        "passes_acceptance": (correct / n if n else 0.0) >= ACCEPTANCE,
        "failures": [(o.question, _diff_note(o)) for o in outcomes if not o.correct],
    }


def _diff_note(o: "QueryOutcome") -> str:
    got = sorted(o.actual) if o.actual is not None else None
    return f"expected {sorted(o.expected)}, got {got}"


def render_report(outcomes: list[QueryOutcome], summary: dict) -> str:
    pct = lambda x: f"{100 * x:.0f}%"
    lines = [
        "# GeoAsk accuracy audit",
        "",
        f"- Queries: **{summary['n']}**",
        f"- Correct maps (exact match vs manual baseline): **{pct(summary['accuracy'])}**",
        f"- Access-gap invariant held: **{pct(summary['invariant_rate'])}**",
        f"- Time-to-answer: mean **{summary['mean_seconds']:.2f}s**, median **{summary['median_seconds']:.2f}s**",
        f"- Acceptance (≥{pct(ACCEPTANCE)} correct): **{'PASS' if summary['passes_acceptance'] else 'FAIL'}**",
        "",
        "| # | Question | Correct | Invariant | Time (s) |",
        "|---|---|:---:|:---:|---:|",
    ]
    for i, o in enumerate(outcomes, 1):
        lines.append(f"| {i} | {o.question} | {'✓' if o.correct else '✗'} | "
                     f"{'✓' if o.invariant_ok else '✗'} | {o.seconds:.2f} |")
    if summary["failures"]:
        lines += ["", "## Where it breaks", ""]
        lines += [f"- **{q}** — {note}" for q, note in summary["failures"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    source = _sample_source()
    client = default_client()
    if client is None:
        print("No live model (set ANTHROPIC_API_KEY). Manual-GIS reference answers:\n")
        for i, (q, expected) in enumerate(reference_table(source), 1):
            print(f"{i:2}. {q}\n    -> {sorted(expected)}")
        print("\nRun with ANTHROPIC_API_KEY set to audit the model against these.")
        return 2

    outcomes = run_audit(client, source)
    summary = summarize(outcomes)
    print(render_report(outcomes, summary))
    return 0 if summary["passes_acceptance"] else 1


if __name__ == "__main__":
    sys.exit(main())
