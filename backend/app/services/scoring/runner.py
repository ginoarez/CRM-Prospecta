from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AiAnalysis, Interaction, Lead
from app.services.scoring import analyzer, signals

_STRICT = "\n\nIMPORTANTE: responde ÚNICAMENTE con el objeto JSON, sin texto adicional."


def run_analysis(db: Session, lead: Lead, provider, *, retries: int = 1) -> AiAnalysis:
    raw = signals.collect_signals(lead.website)
    system, user = analyzer.build_prompt(lead, raw)

    parsed = None
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        prompt = user if attempt == 0 else user + _STRICT
        text = provider.complete(system, prompt)
        try:
            parsed = analyzer.parse_analysis(text)
            break
        except ValueError as exc:
            last_err = exc
    if parsed is None:
        raise last_err  # noqa: RSE102 — propaga el último ValueError

    analysis = AiAnalysis(
        lead_id=lead.id,
        raw_signals=raw,
        model=f"{settings.LLM_PROVIDER}/{settings.LLM_MODEL}",
        **parsed,
    )
    db.add(analysis)
    lead.score = parsed["score"]
    db.add(Interaction(lead_id=lead.id, user_id=lead.owner_id, kind="analisis_ia",
                       content=parsed["summary"]))
    db.commit()
    db.refresh(analysis)
    return analysis
