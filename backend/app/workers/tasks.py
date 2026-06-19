from app.workers.celery_app import celery


@celery.task(name="ping")
def ping() -> str:
    return "pong"


@celery.task(name="analyze_lead")
def analyze_lead(lead_id: str) -> dict:
    from app.core.database import SessionLocal
    from app.models import Lead
    from app.services import llm
    from app.services.scoring.runner import run_analysis

    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if lead is None:
            raise ValueError(f"lead {lead_id} not found")
        analysis = run_analysis(db, lead, llm.get_provider())
        return {"analysis_id": str(analysis.id), "score": analysis.score}
    finally:
        db.close()
