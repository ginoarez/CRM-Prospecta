import uuid


def _template(client, headers, channel="wa"):
    r = client.post("/templates", json={"name": "t", "channel": channel,
                                        "body": "Hola {business_name} de {city}"}, headers=headers)
    return r.json()["id"]


def _lead(client, headers, **over):
    payload = {"business_name": "Gym X", "city": "Bogota", "country": "US", "phone": "(1) 234 567 8900"}
    payload.update(over)
    return client.post("/leads", json=payload, headers=headers).json()["id"]


def test_wa_link_ok(client, auth_headers):
    tid = _template(client, auth_headers)
    lead_id = _lead(client, auth_headers)
    r = client.post(f"/leads/{lead_id}/wa-link", json={"template_id": tid}, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["phone"] == "12345678900"
    assert "Gym X" in body["body"] and "Bogota" in body["body"]
    assert body["url"].startswith("https://wa.me/12345678900?text=")


def test_wa_link_no_phone_422(client, auth_headers):
    tid = _template(client, auth_headers)
    lead_id = _lead(client, auth_headers, phone=None)
    r = client.post(f"/leads/{lead_id}/wa-link", json={"template_id": tid}, headers=auth_headers)
    assert r.status_code == 422


def test_wa_link_template_404(client, auth_headers):
    lead_id = _lead(client, auth_headers)
    r = client.post(f"/leads/{lead_id}/wa-link", json={"template_id": str(uuid.uuid4())}, headers=auth_headers)
    assert r.status_code == 404


def test_wa_link_lead_404(client, auth_headers):
    tid = _template(client, auth_headers)
    r = client.post(f"/leads/{uuid.uuid4()}/wa-link", json={"template_id": tid}, headers=auth_headers)
    assert r.status_code == 404


def test_messages_creates_and_moves_to_contactado(client, auth_headers):
    lead_id = _lead(client, auth_headers)
    r = client.post(f"/leads/{lead_id}/messages",
                    json={"channel": "wa_link", "body": "hola"}, headers=auth_headers)
    assert r.status_code == 201 and r.json()["status"] == "enviado"
    assert client.get(f"/leads/{lead_id}", headers=auth_headers).json()["status"] == "contactado"
    ints = client.get(f"/leads/{lead_id}/interactions", headers=auth_headers).json()
    assert any(i["kind"] == "wa_enviado" for i in ints)
    msgs = client.get(f"/leads/{lead_id}/messages", headers=auth_headers).json()
    assert len(msgs) == 1 and msgs[0]["body"] == "hola"


def test_messages_does_not_regress_advanced_stage(client, auth_headers):
    lead_id = _lead(client, auth_headers)
    client.patch(f"/leads/{lead_id}/stage", json={"status": "ganado"}, headers=auth_headers)
    client.post(f"/leads/{lead_id}/messages", json={"channel": "wa_link", "body": "hola"}, headers=auth_headers)
    assert client.get(f"/leads/{lead_id}", headers=auth_headers).json()["status"] == "ganado"


def test_messages_requires_auth(client):
    assert client.get(f"/leads/{uuid.uuid4()}/messages").status_code == 401
