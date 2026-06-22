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


def test_metrics_weekly_prior_week_bucket(client, auth_headers, db):
    """Lead created 3 weeks ago must land in its own week bucket, not the current one."""
    from datetime import datetime, timedelta

    # Create a lead via the API (lands in the current week by default).
    lead_id = client.post(
        "/leads", json={"business_name": "OldLead"}, headers=auth_headers
    ).json()["id"]

    # Back-date the lead's created_at to ~3 weeks ago using the shared DB session.
    three_weeks_ago = datetime.utcnow() - timedelta(days=21)
    from app.models import Lead as LeadModel

    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).one()
    lead.created_at = three_weeks_ago
    db.commit()

    body = client.get("/dashboard/metrics", headers=auth_headers).json()
    weekly = body["weekly"]

    # Determine the expected Monday 3 weeks back using the DB clock (mirrors service logic).
    from sqlalchemy import func as sa_func

    db_monday = db.query(sa_func.date_trunc("week", sa_func.now())).scalar().date()
    target_week = (db_monday - timedelta(weeks=3)).isoformat()

    # The lead must appear in its prior-week bucket, not the current week.
    bucket = next((p for p in weekly if p["week"] == target_week), None)
    assert bucket is not None, f"Expected week {target_week} not found in series"
    assert bucket["leads"] >= 1, f"Lead not bucketed in {target_week}: {weekly}"

    # Total across the series must still equal the total leads count.
    assert sum(p["leads"] for p in weekly) == body["total_leads"]

    # Current week bucket must NOT contain the back-dated lead.
    current_week_bucket = weekly[-1]
    assert current_week_bucket["leads"] == 0, (
        f"Back-dated lead incorrectly appeared in current week: {current_week_bucket}"
    )
