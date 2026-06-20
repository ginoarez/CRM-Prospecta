from sqlalchemy.orm import Session

from app.models import Interaction, Proposal
from app.services.proposals import generator, render

_STRICT = "\n\nIMPORTANTE: responde ÚNICAMENTE con el objeto JSON, sin texto adicional."


def run_proposal(db: Session, lead, analysis, provider, *, retries: int = 1) -> Proposal:
    system, user = generator.build_prompt(lead, analysis)

    parsed = None
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        prompt = user if attempt == 0 else user + _STRICT
        text = provider.complete(system, prompt)
        try:
            parsed = generator.parse_proposal(text)
            break
        except ValueError as exc:
            last_err = exc
    if parsed is None:
        raise last_err or RuntimeError("LLM output could not be parsed")  # noqa: RSE102

    proposal = Proposal(lead_id=lead.id, content=parsed, price=parsed.get("precio"))
    db.add(proposal)
    db.flush()  # asigna proposal.id antes de renderizar

    proposal.pdf_path = render.render_pdf(proposal, lead)

    resumen = parsed.get("diagnostico") or "Propuesta generada"
    db.add(Interaction(lead_id=lead.id, user_id=lead.owner_id,
                       kind="propuesta_generada", content=resumen))
    db.commit()
    db.refresh(proposal)
    return proposal
