import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Interaction, Lead, LeadStatus, Message, Template, User
from app.schemas.messaging import MessageCreate, MessageOut, WaLinkRequest, WaLinkResponse
from app.services.messaging import wa_link as wa

router = APIRouter(prefix="/leads/{lead_id}", tags=["messaging"])

_PRE_CONTACT = {LeadStatus.nuevo, LeadStatus.calificado}


def _lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


@router.post("/wa-link", response_model=WaLinkResponse)
def wa_link_endpoint(lead_id: uuid.UUID, body: WaLinkRequest, db: Session = Depends(get_db),
                     _: User = Depends(get_current_user)):
    lead = _lead_or_404(db, lead_id)
    template = db.get(Template, body.template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="template not found")
    text = wa.render_template(template.body, lead)
    result = wa.build_wa_link(lead, text)
    if result is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="lead has no valid phone for wa.me")
    return WaLinkResponse(**result)


@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(lead_id: uuid.UUID, body: MessageCreate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    lead = _lead_or_404(db, lead_id)
    msg = Message(lead_id=lead.id, channel=body.channel, direction="out",
                  body=body.body, template_id=body.template_id, status="enviado")
    db.add(msg)
    db.add(Interaction(lead_id=lead.id, user_id=user.id, kind="wa_enviado", content=body.body))
    if lead.status in _PRE_CONTACT:
        lead.status = LeadStatus.contactado
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/messages", response_model=list[MessageOut])
def list_messages(lead_id: uuid.UUID, db: Session = Depends(get_db),
                  _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    return (
        db.query(Message).filter(Message.lead_id == lead_id)
        .order_by(Message.created_at.desc()).all()
    )
