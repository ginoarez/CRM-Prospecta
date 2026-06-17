import uuid
from datetime import datetime

from pydantic import BaseModel


class InteractionCreate(BaseModel):
    kind: str
    content: str | None = None


class InteractionOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    user_id: uuid.UUID | None
    kind: str
    content: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
