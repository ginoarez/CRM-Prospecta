import uuid

import pytest

from app.models import Lead, Template


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", city="Bogotá", industry="gym", email="l@x.com",
                source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@pytest.fixture
def email_template(db):
    t = Template(name="Email", channel="email", subject="Idea para {business_name}",
                 body="Hola {business_name}")
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_preview_renders(client, auth_headers, lead, email_template):
    res = client.post(f"/leads/{lead.id}/email-preview",
                      json={"template_id": str(email_template.id)}, headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["subject"] == "Idea para Gym X"
    assert body["body"] == "Hola Gym X"
    assert body["to"] == "l@x.com"


def test_preview_422_when_no_email(client, auth_headers, db, email_template):
    lead = Lead(business_name="NoEmail", source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    res = client.post(f"/leads/{lead.id}/email-preview",
                      json={"template_id": str(email_template.id)}, headers=auth_headers)
    assert res.status_code == 422


def test_preview_404_template(client, auth_headers, lead):
    res = client.post(f"/leads/{lead.id}/email-preview",
                      json={"template_id": str(uuid.uuid4())}, headers=auth_headers)
    assert res.status_code == 404


def test_send_returns_task(client, auth_headers, lead, monkeypatch):
    from app.services.email import sender
    monkeypatch.setattr(sender, "send_email", lambda to, s, b: None)
    res = client.post(f"/leads/{lead.id}/email",
                      json={"subject": "S", "body": "B"}, headers=auth_headers)
    assert res.status_code == 202
    assert "task_id" in res.json()


def test_send_422_when_no_email(client, auth_headers, db):
    lead = Lead(business_name="NoEmail", source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    res = client.post(f"/leads/{lead.id}/email",
                      json={"subject": "S", "body": "B"}, headers=auth_headers)
    assert res.status_code == 422


def test_send_404_lead(client, auth_headers):
    res = client.post(f"/leads/{uuid.uuid4()}/email",
                      json={"subject": "S", "body": "B"}, headers=auth_headers)
    assert res.status_code == 404


def test_email_requires_auth(client, lead):
    assert client.post(f"/leads/{lead.id}/email", json={"subject": "S", "body": "B"}).status_code == 401
