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


@celery.task(name="generate_proposal")
def generate_proposal(lead_id: str) -> dict:
    from app.core.database import SessionLocal
    from app.models import AiAnalysis, Lead
    from app.services import llm
    from app.services.proposals.runner import run_proposal

    db = SessionLocal()
    try:
        lead = db.get(Lead, lead_id)
        if lead is None:
            raise ValueError(f"lead {lead_id} not found")
        analysis = (
            db.query(AiAnalysis).filter(AiAnalysis.lead_id == lead.id)
            .order_by(AiAnalysis.created_at.desc()).first()
        )
        proposal = run_proposal(db, lead, analysis, llm.get_provider())
        return {
            "proposal_id": str(proposal.id),
            "price": float(proposal.price) if proposal.price is not None else None,
        }
    finally:
        db.close()
