import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Lead, Template, User
from app.schemas.email import (
    EmailPreviewRequest, EmailPreviewResponse, EmailSendRequest, EmailSendResponse,
)
from app.services.messaging.email_compose import render_email
from app.workers.tasks import send_lead_email

router = APIRouter(prefix="/leads/{lead_id}", tags=["email"])


def _lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


def _require_email(lead):
    if not lead.email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="lead has no email")


@router.post("/email-preview", response_model=EmailPreviewResponse)
def email_preview(lead_id: uuid.UUID, body: EmailPreviewRequest, db: Session = Depends(get_db),
                  _: User = Depends(get_current_user)):
    lead = _lead_or_404(db, lead_id)
    _require_email(lead)
    template = db.get(Template, body.template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="template not found")
    subject, rendered = render_email(template, lead)
    return EmailPreviewResponse(subject=subject, body=rendered, to=lead.email)


@router.post("/email", status_code=status.HTTP_202_ACCEPTED, response_model=EmailSendResponse)
def send_email_endpoint(lead_id: uuid.UUID, body: EmailSendRequest, db: Session = Depends(get_db),
                        _: User = Depends(get_current_user)):
    lead = _lead_or_404(db, lead_id)
    _require_email(lead)
    result = send_lead_email.delay(str(lead_id), body.subject, body.body)
    return EmailSendResponse(task_id=result.id, status="pending")
