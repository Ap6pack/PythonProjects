"""Frontend serving + the no-config demo endpoint.

These run with no API key and no database, so the whole Phase 3 surface is
covered in CI: the page is served, its assets resolve, and /ask/demo returns a
real orchestrated result the UI can render.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_page_is_served():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "GeoAsk" in body
    assert 'id="map"' in body
    assert 'id="ask-form"' in body


def test_static_assets_resolve():
    for path in ("/static/app.js", "/static/styles.css"):
        assert client.get(path).status_code == 200


def test_demo_endpoint_returns_orchestrated_result():
    resp = client.post("/ask/demo")
    assert resp.status_code == 200
    data = resp.json()
    assert data["finished"] is True
    # The canned access-gap plan yields the far, above-average-senior tracts.
    names = {f["properties"]["tract"] for f in data["geojson"]["features"]}
    assert names == {"Pleasant Vly", "Powellhurst", "Hazelwood"}
    # Trace is the transparency panel: the full chain, ending in finish.
    tools = [s["tool"] for s in data["trace"]]
    assert tools == ["load_pois", "isochrone", "load_tracts", "spatial_join",
                     "filter_by_attribute", "finish"]
    assert "drive-time" in data["explanation"]


def test_demo_geojson_is_renderable():
    data = client.post("/ask/demo").json()
    feat = data["geojson"]["features"][0]
    assert feat["geometry"]["type"] == "Polygon"
    assert feat["geometry"]["coordinates"]
