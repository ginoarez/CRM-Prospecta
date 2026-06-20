from pydantic import BaseModel


class SuggestReplyRequest(BaseModel):
    objection: str | None = None


class SuggestReplyResponse(BaseModel):
    suggestions: list[str]
