from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Message
from app.services.whatsapp import cloud_api

_WINDOW = timedelta(hours=24)


def _within_window(lead, now: datetime) -> bool:
    if lead.last_inbound_at is None:
        return False
    last = lead.last_inbound_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (now - last) < _WINDOW


def validate_send(lead, payload: dict, now: datetime) -> str | None:
    if lead.whatsapp_opt_out:
        return "el lead se dio de baja (opt-out)"
    if payload.get("template_name"):
        return None
    if payload.get("text"):
        if not _within_window(lead, now):
            return "fuera de la ventana de 24 h: usa una plantilla aprobada"
        return None
    return "se requiere 'text' o 'template_name'"


def run_wa_send(db: Session, lead, payload: dict, now: datetime) -> Message:
    reason = validate_send(lead, payload, now)
    if reason is not None:
        raise ValueError(reason)

    to = "".join(ch for ch in (lead.phone or "") if ch.isdigit())
    is_template = bool(payload.get("template_name"))
    body = payload.get("template_name") if is_template else payload.get("text")
    try:
        if is_template:
            cloud_api.send_template(to, payload["template_name"],
                                    payload.get("language", "es"), payload.get("params"))
        else:
            cloud_api.send_text(to, payload["text"])
    except Exception:
        db.add(Message(lead_id=lead.id, channel="wa_cloud", direction="out",
                       body=body, status="fallido"))
        db.commit()
        raise

    msg = Message(lead_id=lead.id, channel="wa_cloud", direction="out", body=body, status="enviado")
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
