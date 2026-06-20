import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import Interaction, Lead, LeadStatus, Meeting


def _future(days=2):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_create_meeting_persists_logs_and_moves_stage(client, auth_headers, lead, db):
    res = client.post(f"/leads/{lead.id}/meetings",
                      json={"title": "Demo", "scheduled_at": _future(), "duration_minutes": 45},
                      headers=auth_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Demo"
    assert body["status"] == "programada"
    assert body["google_calendar_url"].startswith("https://calendar.google.com")
    assert db.query(Interaction).filter_by(lead_id=lead.id, kind="reunion").count() == 1
    db.refresh(lead)
    assert lead.status == LeadStatus.en_conversacion


def test_create_meeting_does_not_move_won_lead(client, auth_headers, db):
    lead = Lead(business_name="Won", source="manual", status="ganado")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    client.post(f"/leads/{lead.id}/meetings",
                json={"title": "X", "scheduled_at": _future()}, headers=auth_headers)
    db.refresh(lead)
    assert lead.status == LeadStatus.ganado


def test_list_meetings_ordered(client, auth_headers, lead):
    client.post(f"/leads/{lead.id}/meetings", json={"title": "B", "scheduled_at": _future(5)}, headers=auth_headers)
    client.post(f"/leads/{lead.id}/meetings", json={"title": "A", "scheduled_at": _future(1)}, headers=auth_headers)
    res = client.get(f"/leads/{lead.id}/meetings", headers=auth_headers)
    titles = [m["title"] for m in res.json()]
    assert titles == ["A", "B"]


def test_patch_status(client, auth_headers, lead):
    mid = client.post(f"/leads/{lead.id}/meetings", json={"title": "X", "scheduled_at": _future()},
                      headers=auth_headers).json()["id"]
    res = client.patch(f"/meetings/{mid}", json={"status": "realizada"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "realizada"


def test_patch_invalid_status_422(client, auth_headers, lead):
    mid = client.post(f"/leads/{lead.id}/meetings", json={"title": "X", "scheduled_at": _future()},
                      headers=auth_headers).json()["id"]
    res = client.patch(f"/meetings/{mid}", json={"status": "loquesea"}, headers=auth_headers)
    assert res.status_code == 422


def test_delete_meeting(client, auth_headers, lead):
    mid = client.post(f"/leads/{lead.id}/meetings", json={"title": "X", "scheduled_at": _future()},
                      headers=auth_headers).json()["id"]
    assert client.delete(f"/meetings/{mid}", headers=auth_headers).status_code == 204
    assert client.patch(f"/meetings/{mid}", json={"status": "realizada"}, headers=auth_headers).status_code == 404


def test_ics_endpoint(client, auth_headers, lead):
    mid = client.post(f"/leads/{lead.id}/meetings", json={"title": "X", "scheduled_at": _future()},
                      headers=auth_headers).json()["id"]
    res = client.get(f"/meetings/{mid}/ics", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/calendar")
    assert "BEGIN:VEVENT" in res.text


def test_upcoming_only_future_programadas(client, auth_headers, lead, db):
    client.post(f"/leads/{lead.id}/meetings", json={"title": "Fut", "scheduled_at": _future(1)}, headers=auth_headers)
    past = Meeting(lead_id=lead.id, title="Pas",
                   scheduled_at=datetime.now(timezone.utc) - timedelta(days=1), duration_minutes=30,
                   status="programada")
    db.add(past)
    db.commit()
    res = client.get("/meetings/upcoming", headers=auth_headers)
    titles = [m["title"] for m in res.json()]
    assert "Fut" in titles and "Pas" not in titles


def test_create_meeting_lead_404(client, auth_headers):
    res = client.post(f"/leads/{uuid.uuid4()}/meetings",
                      json={"title": "X", "scheduled_at": _future()}, headers=auth_headers)
    assert res.status_code == 404


def test_meetings_require_auth(client, lead):
    assert client.get(f"/leads/{lead.id}/meetings").status_code == 401
