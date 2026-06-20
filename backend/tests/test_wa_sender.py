from datetime import datetime, timedelta, timezone

import pytest

from app.models import Lead, Message
from app.services.whatsapp import cloud_api, sender


def _now():
    return datetime(2026, 6, 20, 12, 0, 0, tzinfo=timezone.utc)


def _lead(db, **kw):
    base = dict(business_name="X", phone="+573001112233", country="CO", source="manual",
                status="en_conversacion")
    base.update(kw)
    lead = Lead(**base)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_validate_text_within_window_ok(db):
    lead = _lead(db, last_inbound_at=_now() - timedelta(hours=1))
    assert sender.validate_send(lead, {"text": "Hola"}, _now()) is None


def test_validate_text_outside_window_blocked(db):
    lead = _lead(db, last_inbound_at=_now() - timedelta(hours=30))
    assert sender.validate_send(lead, {"text": "Hola"}, _now()) is not None


def test_validate_template_always_ok(db):
    lead = _lead(db, last_inbound_at=None)
    assert sender.validate_send(lead, {"template_name": "promo", "language": "es"}, _now()) is None


def test_validate_opt_out_blocked(db):
    lead = _lead(db, whatsapp_opt_out=True, last_inbound_at=_now())
    assert sender.validate_send(lead, {"text": "Hola"}, _now()) is not None


def test_validate_empty_blocked(db):
    lead = _lead(db, last_inbound_at=_now())
    assert sender.validate_send(lead, {}, _now()) is not None


def test_run_wa_send_success_logs_outbound(db, monkeypatch):
    lead = _lead(db, last_inbound_at=_now() - timedelta(hours=1))
    monkeypatch.setattr(cloud_api, "send_text", lambda to, text: {"messages": [{"id": "x"}]})
    msg = sender.run_wa_send(db, lead, {"text": "Hola"}, _now())
    assert msg.channel == "wa_cloud" and msg.direction == "out" and msg.status == "enviado"


def test_run_wa_send_failure_marks_fallido(db, monkeypatch):
    lead = _lead(db, last_inbound_at=_now() - timedelta(hours=1))

    def boom(to, text):
        raise RuntimeError("api down")

    monkeypatch.setattr(cloud_api, "send_text", boom)
    with pytest.raises(RuntimeError):
        sender.run_wa_send(db, lead, {"text": "Hola"}, _now())
    msg = db.query(Message).filter_by(lead_id=lead.id).one()
    assert msg.status == "fallido"
