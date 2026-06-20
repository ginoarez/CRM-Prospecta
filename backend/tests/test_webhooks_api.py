import pytest

from app.core.config import settings
from app.models import Lead, LeadStatus, Message


@pytest.fixture
def lead(db):
    lead = Lead(business_name="X", phone="+573001112233", country="CO", source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def _inbound(text, frm="573001112233"):
    return {"entry": [{"changes": [{"value": {"messages": [
        {"from": frm, "id": "wamid.1", "type": "text", "text": {"body": text}}]}}]}]}


def test_verify_handshake_ok(client, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_VERIFY_TOKEN", "secret")
    res = client.get("/webhooks/whatsapp",
                     params={"hub.mode": "subscribe", "hub.verify_token": "secret", "hub.challenge": "12345"})
    assert res.status_code == 200
    assert res.text == "12345"


def test_verify_handshake_bad_token(client, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_VERIFY_TOKEN", "secret")
    res = client.get("/webhooks/whatsapp",
                     params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "1"})
    assert res.status_code == 403


def test_inbound_logs_and_moves_stage(client, db, lead):
    res = client.post("/webhooks/whatsapp", json=_inbound("Hola me interesa"))
    assert res.status_code == 200
    assert res.json()["received"] == 1
    msg = db.query(Message).filter_by(lead_id=lead.id, direction="in").one()
    assert msg.channel == "wa_cloud" and msg.status == "recibido"
    db.refresh(lead)
    assert lead.status == LeadStatus.en_conversacion
    assert lead.last_inbound_at is not None


def test_inbound_opt_out(client, db, lead):
    client.post("/webhooks/whatsapp", json=_inbound("STOP"))
    db.refresh(lead)
    assert lead.whatsapp_opt_out is True


def test_inbound_garbage_returns_200(client):
    res = client.post("/webhooks/whatsapp", json={"foo": "bar"})
    assert res.status_code == 200
    assert res.json()["received"] == 0


def test_inbound_is_public(client):
    assert client.post("/webhooks/whatsapp", json={}).status_code == 200
