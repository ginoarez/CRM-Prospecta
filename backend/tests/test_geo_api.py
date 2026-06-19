import app.services.geo.nominatim as nom
import app.services.geo.overpass as ov

BBOX = [-34.60, -34.50, -58.50, -58.40]


def _patch_geo(monkeypatch, pois):
    calls = {"nominatim": 0}

    def fake_geocode(location):
        calls["nominatim"] += 1
        return BBOX

    monkeypatch.setattr(nom, "geocode", fake_geocode)
    monkeypatch.setattr(ov, "fetch_pois", lambda bbox, tags: pois)
    return calls


def _poi(osm_id="node/1", name="Gym A"):
    return {"osm_id": osm_id, "name": name, "lat": -34.5, "lng": -58.4,
            "website": None, "phone": None, "address": None}


def test_search_returns_results(client, auth_headers, monkeypatch):
    _patch_geo(monkeypatch, [_poi()])
    r = client.post("/geo/search", json={"location": "Palermo", "category": "gym"}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 1
    assert body["bbox"] == BBOX
    assert body["results"][0]["already_imported"] is False


def test_search_unknown_category_422(client, auth_headers):
    r = client.post("/geo/search", json={"location": "X", "category": "nope"}, headers=auth_headers)
    assert r.status_code == 422


def test_search_location_not_found_404(client, auth_headers, monkeypatch):
    monkeypatch.setattr(nom, "geocode", lambda loc: None)
    monkeypatch.setattr(ov, "fetch_pois", lambda b, t: [])
    r = client.post("/geo/search", json={"location": "Nowhere", "category": "gym"}, headers=auth_headers)
    assert r.status_code == 404


def test_second_search_uses_cache_and_skips_nominatim(client, auth_headers, monkeypatch):
    calls = _patch_geo(monkeypatch, [])
    client.post("/geo/search", json={"location": "Palermo", "category": "gym"}, headers=auth_headers)
    client.post("/geo/search", json={"location": "  palermo ", "category": "gym"}, headers=auth_headers)
    assert calls["nominatim"] == 1  # la 2ª búsqueda reusó el bbox cacheado


def test_search_requires_auth(client):
    assert client.post("/geo/search", json={"location": "X", "category": "gym"}).status_code == 401


def test_import_creates_and_dedupes(client, auth_headers):
    payload = {"items": [
        {"osm_id": "node/10", "name": "Gym A", "lat": -34.5, "lng": -58.4, "category": "gym"},
        {"osm_id": "node/10", "name": "Gym A dup", "lat": -34.5, "lng": -58.4, "category": "gym"},
        {"osm_id": "node/11", "name": "Gym B", "lat": -34.6, "lng": -58.5, "category": "gym"},
    ]}
    r = client.post("/geo/import", json=payload, headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == {"created": 2, "skipped_existing": 1}


def test_import_skips_already_existing_across_calls(client, auth_headers):
    item = {"items": [{"osm_id": "node/20", "name": "X", "lat": 1.0, "lng": 2.0, "category": "gym"}]}
    client.post("/geo/import", json=item, headers=auth_headers)
    r2 = client.post("/geo/import", json=item, headers=auth_headers)
    assert r2.json() == {"created": 0, "skipped_existing": 1}
    # El lead creado tiene source='osm'
    leads = client.get("/leads?q=X", headers=auth_headers).json()["items"]
    assert any(l["source"] == "osm" for l in leads)


def test_imported_lead_marked_already_imported_in_search(client, auth_headers, monkeypatch):
    client.post("/geo/import",
                json={"items": [{"osm_id": "node/30", "name": "Imp", "lat": 1.0, "lng": 2.0, "category": "gym"}]},
                headers=auth_headers)
    _patch_geo(monkeypatch, [_poi(osm_id="node/30", name="Imp")])
    r = client.post("/geo/search", json={"location": "Palermo", "category": "gym"}, headers=auth_headers)
    assert r.json()["results"][0]["already_imported"] is True
