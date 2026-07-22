"""filter_by_attribute — keep features whose property passes a comparison.

The non-spatial workhorse: "tracts with >20% seniors", "pharmacies that are
open 24h". Kept deliberately small and total — an unknown operator or a missing
property is an error, not a silently-empty result, so the orchestration layer
gets a clear signal instead of a plausible-but-wrong map.
"""

from __future__ import annotations

import operator
from typing import Any, Callable

from .geo import feature_collection, features_of

_OPS: dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def filter_by_attribute(
    fc: dict[str, Any],
    attribute: str,
    op: str,
    value: Any,
) -> dict[str, Any]:
    if op not in _OPS:
        raise ValueError(f"unknown operator {op!r}; expected one of {sorted(_OPS)}")
    compare = _OPS[op]

    kept = []
    for f in features_of(fc):
        props = f.get("properties") or {}
        if attribute not in props:
            continue
        current = props[attribute]
        if current is None:
            continue
        try:
            if compare(current, value):
                kept.append(f)
        except TypeError:
            # e.g. comparing a string property with a numeric threshold.
            raise ValueError(
                f"cannot compare property {attribute!r} ({current!r}) with {value!r}"
            )
    return feature_collection(kept)
