import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Interaction, Lead, LeadStatus, Meeting, User
from app.schemas.meeting import MeetingCreate, MeetingOut, MeetingUpdate
from app.services.agenda import calendar_links as cl

router = APIRouter(tags=["agenda"])

_PRE_CONV = {LeadStatus.nuevo, LeadStatus.calificado, LeadStatus.contactado}


def _with_url(meeting, lead) -> dict:
    data = MeetingOut.model_validate(meeting).model_dump()
    data["google_calendar_url"] = cl.google_calendar_url(meeting, lead)
    return data


def _meeting_or_404(db, meeting_id) -> Meeting:
    m = db.get(Meeting, meeting_id)
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="meeting not found")
    return m


@router.post("/leads/{lead_id}/meetings", status_code=status.HTTP_201_CREATED)
def create_meeting(lead_id: uuid.UUID, body: MeetingCreate, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    meeting = Meeting(lead_id=lead.id, title=body.title, scheduled_at=body.scheduled_at,
                      duration_minutes=body.duration_minutes, location=body.location, notes=body.notes)
    db.add(meeting)
    db.add(Interaction(lead_id=lead.id, user_id=user.id, kind="reunion",
                       content=f"{body.title} @ {body.scheduled_at.isoformat()}"))
    if lead.status in _PRE_CONV:
        lead.status = LeadStatus.en_conversacion
    db.commit()
    db.refresh(meeting)
    return _with_url(meeting, lead)


@router.get("/leads/{lead_id}/meetings")
def list_meetings(lead_id: uuid.UUID, db: Session = Depends(get_db),
                  _: User = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    meetings = (
        db.query(Meeting).filter(Meeting.lead_id == lead_id)
        .order_by(Meeting.scheduled_at.asc()).all()
    )
    return [_with_url(m, lead) for m in meetings]


@router.patch("/meetings/{meeting_id}", response_model=MeetingOut)
def update_meeting(meeting_id: uuid.UUID, body: MeetingUpdate, db: Session = Depends(get_db),
                   _: User = Depends(get_current_user)):
    meeting = _meeting_or_404(db, meeting_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(meeting_id: uuid.UUID, db: Session = Depends(get_db),
                   _: User = Depends(get_current_user)):
    meeting = _meeting_or_404(db, meeting_id)
    db.delete(meeting)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/meetings/{meeting_id}/ics")
def meeting_ics(meeting_id: uuid.UUID, db: Session = Depends(get_db),
                _: User = Depends(get_current_user)):
    meeting = _meeting_or_404(db, meeting_id)
    lead = db.get(Lead, meeting.lead_id)
    ics = cl.build_ics(meeting, lead)
    return Response(content=ics, media_type="text/calendar",
                    headers={"Content-Disposition": f'attachment; filename="cita-{meeting_id}.ics"'})


@router.get("/meetings/upcoming")
def upcoming(limit: int = Query(20, le=100), db: Session = Depends(get_db),
             _: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    meetings = (
        db.query(Meeting).filter(Meeting.status == "programada", Meeting.scheduled_at >= now)
        .order_by(Meeting.scheduled_at.asc()).limit(limit).all()
    )
    out = []
    for m in meetings:
        lead = db.get(Lead, m.lead_id)
        out.append(_with_url(m, lead))
    return out
