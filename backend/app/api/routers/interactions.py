import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Interaction, Lead, User
from app.schemas.interaction import InteractionCreate, InteractionOut

router = APIRouter(prefix="/leads/{lead_id}/interactions", tags=["interactions"])


def _lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


@router.get("", response_model=list[InteractionOut])
def list_interactions(lead_id: uuid.UUID, db: Session = Depends(get_db),
                      _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    return (
        db.query(Interaction).filter(Interaction.lead_id == lead_id)
        .order_by(Interaction.created_at.desc()).all()
    )


@router.post("", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
def add_interaction(lead_id: uuid.UUID, body: InteractionCreate, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    obj = Interaction(lead_id=lead_id, user_id=user.id, kind=body.kind, content=body.content)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
