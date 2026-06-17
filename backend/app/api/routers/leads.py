import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import LeadStatus, User
from app.schemas.lead import LeadCreate, LeadList, LeadOut, LeadUpdate, StageUpdate
from app.services import leads as svc

router = APIRouter(prefix="/leads", tags=["leads"])


def _get_or_404(db, lead_id):
    lead = svc.get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


@router.get("", response_model=LeadList)
def list_leads(
    status: LeadStatus | None = None,
    min_score: int | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    items, total = svc.list_leads(
        db, status=status, min_score=min_score, q=q, page=page, page_size=page_size
    )
    return LeadList(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(body: LeadCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return svc.create_lead(db, body.model_dump(), owner_id=user.id)


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return _get_or_404(db, lead_id)


@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: uuid.UUID, body: LeadUpdate, db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    lead = _get_or_404(db, lead_id)
    return svc.update_lead(db, lead, body.model_dump(exclude_unset=True))


@router.patch("/{lead_id}/stage", response_model=LeadOut)
def change_stage(lead_id: uuid.UUID, body: StageUpdate, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    lead = _get_or_404(db, lead_id)
    return svc.change_stage(db, lead, body.status, user.id)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    lead = _get_or_404(db, lead_id)
    svc.delete_lead(db, lead)
