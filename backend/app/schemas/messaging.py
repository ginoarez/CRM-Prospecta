import uuid
from datetime import datetime

from pydantic import BaseModel


class WaLinkRequest(BaseModel):
    template_id: uuid.UUID


class WaLinkResponse(BaseModel):
    url: str
    body: str
    phone: str


class MessageCreate(BaseModel):
    channel: str
    body: str | None = None
    template_id: uuid.UUID | None = None


class MessageOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    channel: str
    direction: str
    body: str | None
    template_id: uuid.UUID | None
    status: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
