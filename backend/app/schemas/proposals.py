import uuid
from datetime import datetime

from pydantic import BaseModel, computed_field


class ProposalOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    content: dict
    price: float | None
    pdf_path: str | None
    created_at: datetime

    @computed_field
    @property
    def pdf_available(self) -> bool:
        return bool(self.pdf_path)

    model_config = {"from_attributes": True}


class ProposalResponse(BaseModel):
    task_id: str
    status: str
