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


def test_metrics_weekly_series(client, auth_headers):
    from datetime import date, timedelta

    for name in ("A", "B", "C"):
        client.post("/leads", json={"business_name": name}, headers=auth_headers)

    body = client.get("/dashboard/metrics", headers=auth_headers).json()

    assert "weekly" in body
    assert len(body["weekly"]) == 8
    # cada punto tiene week (str) y leads (int)
    assert all(set(p.keys()) == {"week", "leads"} for p in body["weekly"])
    # todos creados ahora -> caen en la semana actual (último punto)
    assert sum(p["leads"] for p in body["weekly"]) == 3
    assert body["weekly"][-1]["leads"] == 3

    # Verify week strings are ISO format Monday dates in chronological order
    monday = date.today() - timedelta(days=date.today().weekday())
    assert body["weekly"][0]["week"] == (monday - timedelta(weeks=7)).isoformat()
    assert body["weekly"][-1]["week"] == monday.isoformat()
