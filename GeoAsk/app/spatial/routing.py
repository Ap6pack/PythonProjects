"""Routing backends for the isochrone primitive.

The isochrone needs road-network reachability, which is a routing-engine job.
This module defines a small ``RoutingClient`` protocol and a concrete
``ValhallaClient`` (Valhalla's ``/isochrone`` endpoint returns GeoJSON polygons
directly, so it is the cleanest open engine to target). The primitive depends on
the protocol, not the engine, so the backend is swappable and — importantly —
mockable in tests without a live server.

When no routing engine is configured, the caller falls back to a labelled
straight-line approximation. That fallback is explicit and flagged, never a
silent stand-in for real routing.
"""

from __future__ import annotations

import json
import os
from typing import Any, Protocol, runtime_checkable
from urllib import error, request

# Map GeoAsk travel modes to Valhalla costing models.
_VALHALLA_COSTING = {"walk": "pedestrian", "bike": "bicycle", "drive": "auto"}


@runtime_checkable
class RoutingClient(Protocol):
    """Anything that can turn an origin + time budget into a reachable polygon."""

    def isochrone(self, lon: float, lat: float, minutes: float, mode: str) -> dict[str, Any]:
        """Return a single GeoJSON Polygon/MultiPolygon geometry (a dict) for the
        area reachable from (lon, lat) within ``minutes`` by ``mode``."""
        ...


class ValhallaClient:
    """Talks to a Valhalla routing server's ``/isochrone`` endpoint."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def isochrone(self, lon: float, lat: float, minutes: float, mode: str) -> dict[str, Any]:
        costing = _VALHALLA_COSTING.get(mode)
        if costing is None:
            raise ValueError(f"unknown mode {mode!r}; expected {sorted(_VALHALLA_COSTING)}")

        payload = {
            "locations": [{"lon": lon, "lat": lat}],
            "costing": costing,
            "contours": [{"time": minutes}],
            "polygons": True,
        }
        raw = self._post("/isochrone", payload)
        # Valhalla returns a FeatureCollection with one contour feature.
        features = raw.get("features") or []
        if not features:
            raise RoutingError("routing engine returned no isochrone contour")
        return features[0]["geometry"]

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError) as exc:
            raise RoutingError(f"routing request failed: {exc}") from exc


class RoutingError(RuntimeError):
    """Raised when the routing engine is unreachable or returns nothing usable."""


def default_client() -> RoutingClient | None:
    """Build a routing client from the environment, or ``None`` if unconfigured.

    ``VALHALLA_URL`` selects the Valhalla backend. Absent it, the isochrone
    primitive uses its labelled approximation fallback.
    """
    url = os.environ.get("VALHALLA_URL")
    if url:
        return ValhallaClient(url)
    return None
