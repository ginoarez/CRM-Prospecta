from app.models import Lead
from app.services.phone import normalize_phone

_OPT_OUT = {"STOP", "BAJA", "CANCELAR", "UNSUBSCRIBE", "BAJA TOTAL"}


def parse_inbound(payload: dict) -> list[dict]:
    out: list[dict] = []
    for entry in (payload or {}).get("entry", []) or []:
        for change in entry.get("changes", []) or []:
            value = change.get("value", {}) or {}
            for msg in value.get("messages", []) or []:
                if msg.get("type") == "text":
                    out.append({
                        "from": msg.get("from"),
                        "text": (msg.get("text") or {}).get("body", ""),
                        "wa_id": msg.get("id"),
                    })
    return out


def is_opt_out(text: str) -> bool:
    return (text or "").strip().upper() in _OPT_OUT


def find_lead_by_phone(db, from_digits: str):
    target = normalize_phone(f"+{from_digits}", None)
    if target is None:
        return None
    for lead in db.query(Lead).filter(Lead.phone.isnot(None)).all():
        if normalize_phone(lead.phone, lead.country) == target:
            return lead
    return None
