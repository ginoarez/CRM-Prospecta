from pydantic import BaseModel


class WaSendRequest(BaseModel):
    text: str | None = None
    template_name: str | None = None
    language: str = "es"
    params: list[str] | None = None


class WaSendResponse(BaseModel):
    task_id: str
    status: str
