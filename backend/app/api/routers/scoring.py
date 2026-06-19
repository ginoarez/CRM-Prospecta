import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import AiAnalysis, Lead, User
from app.schemas.scoring import AnalysisOut, AnalyzeResponse
from app.workers.tasks import analyze_lead

router = APIRouter(prefix="/leads/{lead_id}", tags=["scoring"])


def _lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED, response_model=AnalyzeResponse)
def analyze(lead_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    result = analyze_lead.delay(str(lead_id))
    return AnalyzeResponse(task_id=result.id, status="pending")


@router.get("/analysis", response_model=AnalysisOut | None)
def latest_analysis(lead_id: uuid.UUID, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    return (
        db.query(AiAnalysis).filter(AiAnalysis.lead_id == lead_id)
        .order_by(AiAnalysis.created_at.desc()).first()
    )
