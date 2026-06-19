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
