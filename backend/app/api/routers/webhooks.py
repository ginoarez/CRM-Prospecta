from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import LeadStatus, Message
from app.services.whatsapp import inbound

router = APIRouter(prefix="/webhooks/whatsapp", tags=["webhooks"])

_PRE_CONV = {LeadStatus.nuevo, LeadStatus.calificado, LeadStatus.contactado}


@router.get("")
def verify(request: Request):
    params = request.query_params
    if (params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN
            and settings.WHATSAPP_VERIFY_TOKEN):
        return PlainTextResponse(params.get("hub.challenge", ""))
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.post("")
async def incoming(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    messages = inbound.parse_inbound(payload)
    now = datetime.now(timezone.utc)
    count = 0
    for m in messages:
        lead = inbound.find_lead_by_phone(db, m["from"] or "")
        if lead is None:
            continue
        db.add(Message(lead_id=lead.id, channel="wa_cloud", direction="in",
                       body=m["text"], status="recibido"))
        lead.last_inbound_at = now
        if lead.status in _PRE_CONV:
            lead.status = LeadStatus.en_conversacion
        if inbound.is_opt_out(m["text"]):
            lead.whatsapp_opt_out = True
        count += 1
    db.commit()
    return {"received": count}
