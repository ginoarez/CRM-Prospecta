import uuid

from pydantic import BaseModel


class EmailPreviewRequest(BaseModel):
    template_id: uuid.UUID


class EmailPreviewResponse(BaseModel):
    subject: str
    body: str
    to: str


class EmailSendRequest(BaseModel):
    subject: str
    body: str
    template_id: uuid.UUID | None = None


class EmailSendResponse(BaseModel):
    task_id: str
    status: str
