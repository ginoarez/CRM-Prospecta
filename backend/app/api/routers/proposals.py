import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Lead, Proposal, User
from app.schemas.proposals import ProposalOut, ProposalResponse
from app.workers.tasks import generate_proposal

router = APIRouter(tags=["proposals"])


def _lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="lead not found")
    return lead


@router.post("/leads/{lead_id}/proposals", status_code=status.HTTP_202_ACCEPTED,
             response_model=ProposalResponse)
def create_proposal(lead_id: uuid.UUID, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    result = generate_proposal.delay(str(lead_id))
    return ProposalResponse(task_id=result.id, status="pending")


@router.get("/leads/{lead_id}/proposals", response_model=ProposalOut | None)
def latest_proposal(lead_id: uuid.UUID, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    _lead_or_404(db, lead_id)
    return (
        db.query(Proposal).filter(Proposal.lead_id == lead_id)
        .order_by(Proposal.created_at.desc()).first()
    )


@router.get("/proposals/{proposal_id}/pdf")
def proposal_pdf(proposal_id: uuid.UUID, db: Session = Depends(get_db),
                 _: User = Depends(get_current_user)):
    proposal = db.get(Proposal, proposal_id)
    if proposal is None or not proposal.pdf_path or not os.path.exists(proposal.pdf_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="pdf not found")
    return FileResponse(
        proposal.pdf_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="propuesta-{proposal_id}.pdf"'},
    )
