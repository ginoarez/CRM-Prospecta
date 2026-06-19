import app.services.geo.overpass as ov


def test_parse_elements_nodes_ways_and_discards():
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
    q = ov.build_query([-34.6, -34.5, -58.5, -58.4], [("amenity", "restaurant")])
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
    monkeypatch.setattr(ov.httpx, "post", lambda url, **kw: FakeResp())
    pois = ov.fetch_pois([-1, 1, -1, 1], [("amenity", "cafe")])
    assert pois == [{"osm_id": "node/1", "name": "X", "lat": 1.0, "lng": 2.0,
                     "website": None, "phone": None, "address": None}]
