import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Lead, Message, User
from app.schemas.assistant import SuggestReplyRequest, SuggestReplyResponse
from app.services import llm
from app.services.assistant import objections

router = APIRouter(prefix="/leads/{lead_id}", tags=["assistant"])

_RECENT = 10


@router.post("/suggest-reply", response_model=SuggestReplyResponse)
def suggest_reply(lead_id: uuid.UUID, body: SuggestReplyRequest, db: Session = Depends(get_db),
                  _: User = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    recent = (
        db.query(Message).filter(Message.lead_id == lead_id)
        .order_by(Message.created_at.desc()).limit(_RECENT).all()
    )
    recent.reverse()  # cronológico ascendente
    system, user = objections.build_prompt(lead, recent, body.objection)
    text = llm.get_provider().complete(system, user)
    return SuggestReplyResponse(suggestions=objections.parse_suggestions(text))
