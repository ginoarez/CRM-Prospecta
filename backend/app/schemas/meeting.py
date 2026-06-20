import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

MeetingStatus = Literal["programada", "realizada", "cancelada"]


class MeetingCreate(BaseModel):
    title: str
    scheduled_at: datetime
    duration_minutes: int = 30
    location: str | None = None
    notes: str | None = None


class MeetingUpdate(BaseModel):
    title: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    location: str | None = None
    notes: str | None = None
    status: MeetingStatus | None = None


class MeetingOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    title: str
    scheduled_at: datetime
    duration_minutes: int
    location: str | None
    notes: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
