def _make(client, headers, **over):
    payload = {"business_name": "Gym X", "city": "Bogota", "country": "CO"}
    payload.update(over)
    return client.post("/leads", json=payload, headers=headers)


def test_create_and_get_lead(client, auth_headers):
    r = _make(client, auth_headers)
    assert r.status_code == 201
    lead_id = r.json()["id"]
    assert r.json()["status"] == "nuevo"
    g = client.get(f"/leads/{lead_id}", headers=auth_headers)
    assert g.status_code == 200
    assert g.json()["business_name"] == "Gym X"


def test_create_normalizes_phone(client, auth_headers):
    r = _make(client, auth_headers, phone="(1) 234 567 8900", country="US")
    assert r.json()["phone"] == "+12345678900"


def test_list_filters_by_status_and_query(client, auth_headers):
    _make(client, auth_headers, business_name="Alpha")
    _make(client, auth_headers, business_name="Beta")
    r = client.get("/leads?q=Alph", headers=auth_headers)
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["business_name"] == "Alpha"


def test_update_and_delete(client, auth_headers):
    lead_id = _make(client, auth_headers).json()["id"]
    u = client.patch(f"/leads/{lead_id}", json={"notes": "hi"}, headers=auth_headers)
    assert u.json()["notes"] == "hi"
    d = client.delete(f"/leads/{lead_id}", headers=auth_headers)
    assert d.status_code == 204
    assert client.get(f"/leads/{lead_id}", headers=auth_headers).status_code == 404


def test_list_requires_auth(client):
    assert client.get("/leads").status_code == 401
