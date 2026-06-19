import uuid
from datetime import datetime

from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    channel: str
    body: str


class TemplateUpdate(BaseModel):
    name: str | None = None
    channel: str | None = None
    body: str | None = None


class TemplateOut(BaseModel):
    id: uuid.UUID
    name: str
    channel: str
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
