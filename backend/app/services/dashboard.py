from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Lead, LeadStatus


def _weekly_new_leads(db: Session, weeks: int = 8) -> list[dict]:
    rows = (
        db.query(
            func.date_trunc("week", Lead.created_at).label("week"),
            func.count(Lead.id),
        )
        .group_by("week")
        .all()
    )
    counts = {row[0].date().isoformat(): row[1] for row in rows}

    # anchor = Monday of the current week, computed on the DB clock so the
    # keys match date_trunc('week', created_at) regardless of server timezone.
    monday = db.query(func.date_trunc("week", func.now())).scalar().date()
    series: list[dict] = []
    for i in range(weeks - 1, -1, -1):  # del más viejo al más nuevo
        wk = (monday - timedelta(weeks=i)).isoformat()
        series.append({"week": wk, "leads": counts.get(wk, 0)})
    return series


def metrics(db: Session) -> dict:
    by_status = {s.value: 0 for s in LeadStatus}
    rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    for status_value, count in rows:
        key = status_value.value if hasattr(status_value, "value") else str(status_value)
        by_status[key] = count
    return {
        "total_leads": sum(by_status.values()),
        "by_status": by_status,
        "weekly": _weekly_new_leads(db),
    }
