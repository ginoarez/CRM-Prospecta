import app.services.geo.overpass as overpass


def test_details_extracted_from_tags():
    els = [{"type": "node", "id": 1, "lat": 25.67, "lon": -100.31, "tags": {
        "name": "SmartFitness", "leisure": "fitness_centre",
        "opening_hours": "Mo-Fr 06:00-22:00; Sa 08:00-14:00",
        "brand": "SmartFit", "contact:email": "hola@smartfitness.mx",
        "contact:instagram": "@smartfitness.mty", "contact:facebook": "smartfitnessmty",
        "wheelchair": "yes", "delivery": "no", "takeaway": "yes",
    }}]
    out = overpass.parse_elements(els)
    d = out[0]["details"]
    assert d["category"] == "fitness_centre"
    assert d["opening_hours"] == "Mo-Fr 06:00-22:00; Sa 08:00-14:00"
    assert d["brand"] == "SmartFit"
    assert d["email"] == "hola@smartfitness.mx"
    assert d["instagram"] == "@smartfitness.mty"
    assert d["facebook"] == "smartfitnessmty"
    assert d["wheelchair"] == "yes"
    assert d["delivery"] is False
    assert d["takeaway"] is True


def test_details_category_priority_and_missing_tags():
    els = [{"type": "node", "id": 2, "lat": 1.0, "lon": 2.0, "tags": {
        "name": "Tacos X", "cuisine": "mexican", "amenity": "restaurant"}}]
    d = overpass.parse_elements(els)[0]["details"]
    assert d["category"] == "mexican"      # cuisine > shop > amenity > leisure
    assert d["opening_hours"] is None
    assert d["delivery"] is None           # tag ausente -> None (no False)


def test_google_maps_url_urlencoded():
    els = [{"type": "node", "id": 3, "lat": 25.5, "lon": -100.25,
            "tags": {"name": "Café & Té"}}]
    url = overpass.parse_elements(els)[0]["google_maps_url"]
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "Caf%C3%A9%20%26%20T%C3%A9" in url
    assert "25.5%2C-100.25" in url or "25.5,-100.25" in url.replace("%2C", ",")


def test_parse_elements_nodes_ways_and_discards():
    ov = overpass
    elements = [
        {"type": "node", "id": 1, "lat": -34.5, "lon": -58.4,
         "tags": {"name": "Gym A", "phone": "+5411", "addr:street": "Calle 1", "addr:city": "BA"}},
        {"type": "way", "id": 2, "center": {"lat": -34.6, "lon": -58.5},
         "tags": {"name": "Gym B", "website": "http://b.com"}},
        {"type": "node", "id": 3, "lat": -34.7, "lon": -58.6, "tags": {}},          # sin name -> descartado
        {"type": "way", "id": 4, "tags": {"name": "Sin centro"}},                    # sin center -> descartado
    ]
    out = ov.parse_elements(elements)
    assert len(out) == 2
    assert out[0]["osm_id"] == "node/1"
    assert out[0]["phone"] == "+5411"
    assert out[0]["address"] == "Calle 1, BA"
    assert out[1]["osm_id"] == "way/2"
    assert out[1]["lat"] == -34.6 and out[1]["website"] == "http://b.com"


def test_build_query_includes_bbox_and_tags():
    q = overpass.build_query([-34.6, -34.5, -58.5, -58.4], [("amenity", "restaurant")])
    assert "out:json" in q
    assert '["amenity"="restaurant"]' in q
    assert "out center" in q


def test_fetch_pois_calls_overpass(monkeypatch):
    class FakeResp:
        status_code = 200
        def json(self):
            return {"elements": [{"type": "node", "id": 1, "lat": 1.0, "lon": 2.0,
                                  "tags": {"name": "X"}}]}
        def raise_for_status(self):
            return None
    monkeypatch.setattr(overpass.httpx, "post", lambda url, **kw: FakeResp())
    pois = overpass.fetch_pois([-1, 1, -1, 1], [("amenity", "cafe")])
    assert len(pois) == 1
    assert pois[0]["osm_id"] == "node/1"
    assert pois[0]["name"] == "X"
    assert pois[0]["lat"] == 1.0
    assert pois[0]["lng"] == 2.0
    assert pois[0]["website"] is None
    assert pois[0]["phone"] is None
    assert pois[0]["address"] is None
    assert "details" in pois[0]
    assert "google_maps_url" in pois[0]
