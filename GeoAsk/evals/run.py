"""Run the phrasing corpus against the real orchestrator and print a scorecard.

Requires a live LLM (ANTHROPIC_API_KEY). Runs each phrasing over the in-memory
demo sample — so it measures the model's *planning* quality in isolation, with no
database needed:

    ANTHROPIC_API_KEY=... python -m evals.run

The Phase 4 target is that the top phrasings all resolve to a correct access-gap
map without hand-holding; Phase 5 turns this into the documented accuracy audit.
"""

from __future__ import annotations

import sys

from app.orchestration import ask
from app.orchestration.demo import _sample_source
from app.orchestration.llm import default_client

from .phrasings import PHRASINGS, score


def main() -> int:
    client = default_client()
    if client is None:
        print("No LLM configured (set ANTHROPIC_API_KEY). Nothing to run.")
        return 2

    source = _sample_source()
    passed = 0
    for meta in PHRASINGS:
        result = ask(meta["q"], client, source)
        ok, reason = score(meta, result)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {meta['q']}\n        {reason}")

    total = len(PHRASINGS)
    print(f"\n{passed}/{total} phrasings correct ({100 * passed // total}%).")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
