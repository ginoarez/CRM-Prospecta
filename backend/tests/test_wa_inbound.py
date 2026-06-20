from app.models import Lead
from app.services.whatsapp import inbound


_PAYLOAD = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [
                    {"from": "573001112233", "id": "wamid.1", "type": "text", "text": {"body": "Hola"}},
                    {"from": "573009998877", "id": "wamid.2", "type": "image", "image": {"id": "x"}},
                ]
            }
        }]
    }]
}


def test_parse_inbound_returns_text_messages_only():
    msgs = inbound.parse_inbound(_PAYLOAD)
    assert len(msgs) == 1
    assert msgs[0]["from"] == "573001112233"
    assert msgs[0]["text"] == "Hola"


def test_parse_inbound_tolerates_empty():
    assert inbound.parse_inbound({}) == []
    assert inbound.parse_inbound({"entry": [{}]}) == []


def test_is_opt_out():
    assert inbound.is_opt_out("STOP")
    assert inbound.is_opt_out(" baja ")
    assert inbound.is_opt_out("Cancelar")
    assert not inbound.is_opt_out("hola, me interesa")


def test_find_lead_by_phone(db):
    lead = Lead(business_name="X", phone="+57 300 111 2233", country="CO", source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    found = inbound.find_lead_by_phone(db, "573001112233")
    assert found is not None and found.id == lead.id
    assert inbound.find_lead_by_phone(db, "10000000000") is None
