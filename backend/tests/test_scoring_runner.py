import uuid

import app.services.scoring.signals as sig
from app.models import AiAnalysis, Interaction, Lead, User
from app.services.scoring.runner import run_analysis

VALID = '{"score": 80, "needs": ["web"], "urgency": "alta", "buy_probability": 70, ' \
        '"detected_problems": ["x"], "opportunities": ["y"], "summary": "resumen ok"}'


class FakeProvider:
    def __init__(self, text):
        self._text = text
        self.calls = 0

    def complete(self, system, user):
        self.calls += 1
        return self._text


def _make_lead(db):
    user = User(id=uuid.uuid4(), email=f"{uuid.uuid4()}@a.com", password_hash="x", role="agent")
    db.add(user)
    db.flush()  # ensure user row exists before FK reference
    lead = Lead(owner_id=user.id, business_name="Gym X", website=None)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_run_analysis_persists(db, monkeypatch):
    monkeypatch.setattr(sig, "fetch_html", lambda w: None)  # sin web
    lead = _make_lead(db)
    analysis = run_analysis(db, lead, FakeProvider(VALID))
    assert analysis.score == 80
    assert analysis.raw_signals == {"website_reachable": False}
    db.refresh(lead)
    assert lead.score == 80
    assert db.query(AiAnalysis).filter_by(lead_id=lead.id).count() == 1
    assert db.query(Interaction).filter_by(lead_id=lead.id, kind="analisis_ia").count() == 1


def test_run_analysis_retries_then_succeeds(db, monkeypatch):
    monkeypatch.setattr(sig, "fetch_html", lambda w: None)
    lead = _make_lead(db)

    class FlakyProvider:
        def __init__(self):
            self.calls = 0

        def complete(self, system, user):
            self.calls += 1
            return "no json" if self.calls == 1 else VALID

    provider = FlakyProvider()
    analysis = run_analysis(db, lead, provider)
    assert provider.calls == 2
    assert analysis.score == 80
