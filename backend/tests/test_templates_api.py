def test_template_crud(client, auth_headers):
    r = client.post("/templates", json={"name": "t1", "channel": "wa", "body": "hi {business_name}"},
                    headers=auth_headers)
    assert r.status_code == 201
    tid = r.json()["id"]
    listed = client.get("/templates", headers=auth_headers).json()
    assert any(t["id"] == tid for t in listed)
    u = client.patch(f"/templates/{tid}", json={"name": "t2"}, headers=auth_headers)
    assert u.status_code == 200 and u.json()["name"] == "t2"
    assert client.delete(f"/templates/{tid}", headers=auth_headers).status_code == 204
    assert client.delete(f"/templates/{tid}", headers=auth_headers).status_code == 404


def test_template_channel_filter(client, auth_headers):
    client.post("/templates", json={"name": "w", "channel": "wa", "body": "x"}, headers=auth_headers)
    client.post("/templates", json={"name": "e", "channel": "email", "body": "y"}, headers=auth_headers)
    wa = client.get("/templates?channel=wa", headers=auth_headers).json()
    assert wa and all(t["channel"] == "wa" for t in wa)


def test_templates_requires_auth(client):
    assert client.get("/templates").status_code == 401
