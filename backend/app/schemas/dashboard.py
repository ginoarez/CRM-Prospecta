from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_leads: int
    by_status: dict[str, int]
