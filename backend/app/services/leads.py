import uuid

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import Interaction, Lead, LeadStatus
from app.services.phone import normalize_phone


def create_lead(db: Session, data: dict, owner_id: uuid.UUID) -> Lead:
    if data.get("phone"):
        data["phone"] = normalize_phone(data["phone"], data.get("country"))
    lead = Lead(owner_id=owner_id, **data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: uuid.UUID) -> Lead | None:
    return db.get(Lead, lead_id)


def list_leads(db: Session, *, status: LeadStatus | None, min_score: int | None,
               q: str | None, page: int, page_size: int) -> tuple[list[Lead], int]:
    query = db.query(Lead)
    if status is not None:
        query = query.filter(Lead.status == status)
    if min_score is not None:
        query = query.filter(Lead.score >= min_score)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Lead.business_name.ilike(like), Lead.city.ilike(like)))
    total = query.with_entities(func.count(Lead.id)).scalar()
    items = (
        query.order_by(Lead.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return items, total


def update_lead(db: Session, lead: Lead, data: dict) -> Lead:
    if "phone" in data and data["phone"]:
        data["phone"] = normalize_phone(data["phone"], data.get("country") or lead.country)
    for k, v in data.items():
        setattr(lead, k, v)
    db.commit()
    db.refresh(lead)
    return lead


def change_stage(db: Session, lead: Lead, new_status: LeadStatus, user_id: uuid.UUID) -> Lead:
    old = lead.status
    lead.status = new_status
    db.add(Interaction(
        lead_id=lead.id, user_id=user_id, kind="cambio_etapa",
        content=f"{old.value} -> {new_status.value}",
    ))
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead: Lead) -> None:
    db.delete(lead)
    db.commit()
