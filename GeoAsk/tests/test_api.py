from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_lists_primitives():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert any("buffer" in p for p in body["primitives"])


def test_buffer_endpoint(one_pharmacy):
    resp = client.post("/tools/buffer", json={"features": one_pharmacy, "distance_m": 500})
    assert resp.status_code == 200
    assert resp.json()["features"][0]["geometry"]["type"] == "Polygon"


def test_buffer_endpoint_rejects_bad_distance(one_pharmacy):
    resp = client.post("/tools/buffer", json={"features": one_pharmacy, "distance_m": -1})
    # Pydantic gt=0 constraint -> 422 before the primitive runs.
    assert resp.status_code == 422


def test_filter_endpoint(square_tracts):
    resp = client.post(
        "/tools/filter_by_attribute",
        json={"features": square_tracts, "attribute": "pct_senior", "op": ">", "value": 20},
    )
    assert resp.status_code == 200
    assert len(resp.json()["features"]) == 1
