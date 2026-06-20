import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.models import Lead


def _lead(db, **kw):
    base = dict(business_name="X", phone="+573001112233", country="CO", source="manual",
                status="en_conversacion")
    base.update(kw)
    lead = Lead(**base)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@pytest.fixture(autouse=True)
def _no_meta(monkeypatch):
    from app.services.whatsapp import cloud_api
    monkeypatch.setattr(cloud_api, "send_text", lambda to, text: {"messages": [{"id": "x"}]})
    monkeypatch.setattr(cloud_api, "send_template", lambda to, n, l, p=None: {"messages": [{"id": "x"}]})


def test_send_text_within_window_202(client, auth_headers, db):
    lead = _lead(db, last_inbound_at=datetime.now(timezone.utc) - timedelta(hours=1))
    res = client.post(f"/leads/{lead.id}/wa-send", json={"text": "Hola"}, headers=auth_headers)
    assert res.status_code == 202
    assert "task_id" in res.json()


def test_send_text_outside_window_422(client, auth_headers, db):
    lead = _lead(db, last_inbound_at=datetime.now(timezone.utc) - timedelta(hours=30))
    res = client.post(f"/leads/{lead.id}/wa-send", json={"text": "Hola"}, headers=auth_headers)
    assert res.status_code == 422


def test_send_template_outside_window_202(client, auth_headers, db):
    lead = _lead(db, last_inbound_at=None)
    res = client.post(f"/leads/{lead.id}/wa-send",
                      json={"template_name": "promo", "language": "es"}, headers=auth_headers)
    assert res.status_code == 202


def test_send_opt_out_422(client, auth_headers, db):
    lead = _lead(db, whatsapp_opt_out=True, last_inbound_at=datetime.now(timezone.utc))
    res = client.post(f"/leads/{lead.id}/wa-send", json={"text": "Hola"}, headers=auth_headers)
    assert res.status_code == 422


def test_send_404(client, auth_headers):
    res = client.post(f"/leads/{uuid.uuid4()}/wa-send", json={"text": "Hola"}, headers=auth_headers)
    assert res.status_code == 404


def test_send_requires_auth(client, db):
    lead = _lead(db)
    assert client.post(f"/leads/{lead.id}/wa-send", json={"text": "Hola"}).status_code == 401
