import uuid
from datetime import datetime

from pydantic import BaseModel


class AnalysisOut(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    score: int | None
    needs: list
    urgency: str | None
    buy_probability: float | None
    detected_problems: list
    opportunities: list
    summary: str | None
    raw_signals: dict
    model: str | None
    created_at: datetime

    model_config = {"from_attributes": True, "protected_namespaces": ()}


class AnalyzeResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusOut(BaseModel):
    task_id: str
    status: str
    error: str | None = None
