from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus


def metrics(db: Session) -> dict:
    by_status = {s.value: 0 for s in LeadStatus}
    rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    for status_value, count in rows:
        key = status_value.value if hasattr(status_value, "value") else str(status_value)
        by_status[key] = count
    return {"total_leads": sum(by_status.values()), "by_status": by_status}
