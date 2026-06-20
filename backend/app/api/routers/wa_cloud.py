import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Lead, User
from app.schemas.whatsapp import WaSendRequest, WaSendResponse
from app.services.whatsapp import sender
from app.workers.tasks import send_wa_cloud

router = APIRouter(prefix="/leads/{lead_id}", tags=["wa-cloud"])


@router.post("/wa-send", status_code=status.HTTP_202_ACCEPTED, response_model=WaSendResponse)
def wa_send(lead_id: uuid.UUID, body: WaSendRequest, db: Session = Depends(get_db),
            _: User = Depends(get_current_user)):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    payload = body.model_dump()
    reason = sender.validate_send(lead, payload, datetime.now(timezone.utc))
    if reason is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=reason)
    result = send_wa_cloud.delay(str(lead_id), payload)
    return WaSendResponse(task_id=result.id, status="pending")
