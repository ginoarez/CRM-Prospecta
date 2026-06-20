import pytest

from app.models import Interaction, Lead, Proposal
from app.services.proposals import render, runner

_JSON = ('{"diagnostico": "d", "problemas": ["p"], "oportunidades": ["o"], '
         '"soluciones": ["s"], "beneficios": ["b"], "tiempo_estimado": "4 semanas", '
         '"precio": 2500, "roi_estimado": "3x"}')


class FakeProvider:
    def __init__(self, *replies):
        self._replies = list(replies)

    def complete(self, system, user):
        return self._replies.pop(0)


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", city="Bogotá", industry="gym",
                source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_run_proposal_persists_and_renders(db, lead, monkeypatch):
    monkeypatch.setattr(render, "render_pdf", lambda p, l, **k: f"storage/proposals/{p.id}.pdf")
    proposal = runner.run_proposal(db, lead, None, FakeProvider(_JSON))

    assert isinstance(proposal, Proposal)
    assert proposal.content["diagnostico"] == "d"
    assert float(proposal.price) == 2500.0
    assert proposal.pdf_path.endswith(f"{proposal.id}.pdf")

    interactions = db.query(Interaction).filter_by(lead_id=lead.id).all()
    assert any(i.kind == "propuesta_generada" for i in interactions)
    db.refresh(lead)
    assert lead.status.value == "nuevo"  # no cambia la etapa


def test_run_proposal_without_analysis_ok(db, lead, monkeypatch):
    monkeypatch.setattr(render, "render_pdf", lambda p, l, **k: "x.pdf")
    proposal = runner.run_proposal(db, lead, None, FakeProvider(_JSON))
    assert proposal.content["diagnostico"] == "d"


def test_run_proposal_retries_on_bad_json(db, lead, monkeypatch):
    monkeypatch.setattr(render, "render_pdf", lambda p, l, **k: "x.pdf")
    proposal = runner.run_proposal(db, lead, None, FakeProvider("no json", _JSON))
    assert proposal.content["diagnostico"] == "d"


def test_run_proposal_fails_after_retries(db, lead, monkeypatch):
    monkeypatch.setattr(render, "render_pdf", lambda p, l, **k: "x.pdf")
    with pytest.raises(ValueError):
        runner.run_proposal(db, lead, None, FakeProvider("nope", "still nope"))
