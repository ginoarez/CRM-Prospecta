import uuid

import pytest

from app.models import Lead, Message


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", city="Bogotá", industry="gym", source="manual",
                status="en_conversacion")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


class FakeProvider:
    last_user = None

    def complete(self, system, user):
        FakeProvider.last_user = user
        return '["Respuesta uno", "Respuesta dos"]'


def _patch_llm(monkeypatch):
    from app.services import llm
    monkeypatch.setattr(llm, "get_provider", lambda: FakeProvider())


def test_suggest_reply_returns_suggestions(client, auth_headers, lead, db, monkeypatch):
    _patch_llm(monkeypatch)
    db.add(Message(lead_id=lead.id, channel="wa_cloud", direction="in", body="Está muy caro",
                   status="recibido"))
    db.commit()
    res = client.post(f"/leads/{lead.id}/suggest-reply",
                      json={"objection": "precio"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["suggestions"] == ["Respuesta uno", "Respuesta dos"]
    assert "Está muy caro" in FakeProvider.last_user  # usó la conversación


def test_suggest_reply_empty_body_ok(client, auth_headers, lead, monkeypatch):
    _patch_llm(monkeypatch)
    res = client.post(f"/leads/{lead.id}/suggest-reply", json={}, headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()["suggestions"]) >= 1


def test_suggest_reply_404(client, auth_headers, monkeypatch):
    _patch_llm(monkeypatch)
    res = client.post(f"/leads/{uuid.uuid4()}/suggest-reply", json={}, headers=auth_headers)
    assert res.status_code == 404


def test_suggest_reply_requires_auth(client, lead):
    assert client.post(f"/leads/{lead.id}/suggest-reply", json={}).status_code == 401
