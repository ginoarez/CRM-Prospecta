def test_metrics_funnel(client, auth_headers):
    for name in ("A", "B"):
        client.post("/leads", json={"business_name": name}, headers=auth_headers)
    lead_id = client.post("/leads", json={"business_name": "C"}, headers=auth_headers).json()["id"]
    client.patch(f"/leads/{lead_id}/stage", json={"status": "ganado"}, headers=auth_headers)

    r = client.get("/dashboard/metrics", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total_leads"] == 3
    assert body["by_status"]["nuevo"] == 2
    assert body["by_status"]["ganado"] == 1


def test_metrics_requires_auth(client):
    assert client.get("/dashboard/metrics").status_code == 401
