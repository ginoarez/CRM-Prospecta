import pytest

from app.models import Interaction, Lead, LeadStatus, Message
from app.services.email import sender
from app.workers.tasks import send_lead_email


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", city="Bogotá", industry="gym", email="l@x.com",
                source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_send_lead_email_success(db, lead, monkeypatch):
    sent = {}
    monkeypatch.setattr(sender, "send_email", lambda to, s, b: sent.update(to=to, s=s, b=b))

    out = send_lead_email.run(str(lead.id), "Asunto", "Cuerpo")
    assert out["status"] == "enviado"
    assert sent["to"] == "l@x.com"

    msg = db.query(Message).filter_by(lead_id=lead.id).one()
    assert msg.channel == "email" and msg.status == "enviado"
    assert db.query(Interaction).filter_by(lead_id=lead.id, kind="email").count() == 1
    db.refresh(lead)
    assert lead.status == LeadStatus.contactado


def test_send_lead_email_failure_marks_fallido(db, lead, monkeypatch):
    def boom(to, s, b):
        raise RuntimeError("smtp down")
    monkeypatch.setattr(sender, "send_email", boom)

    with pytest.raises(RuntimeError):
        send_lead_email.run(str(lead.id), "Asunto", "Cuerpo")

    msg = db.query(Message).filter_by(lead_id=lead.id).one()
    assert msg.status == "fallido"
    db.refresh(lead)
    assert lead.status == LeadStatus.nuevo  # no avanza en fallo
