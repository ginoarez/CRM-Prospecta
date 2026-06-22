from pydantic import BaseModel


class WeeklyPoint(BaseModel):
    week: str
    leads: int


class DashboardMetrics(BaseModel):
    total_leads: int
    by_status: dict[str, int]
    weekly: list[WeeklyPoint]
