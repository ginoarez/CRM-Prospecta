import uuid

import pytest

from app.models import Lead, Proposal


@pytest.fixture
def lead(db):
    lead = Lead(business_name="Gym X", city="Bogotá", industry="gym",
                source="manual", status="nuevo")
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def test_post_proposal_returns_task(client, auth_headers, lead, monkeypatch):
    from app.services import llm
    from app.services.proposals import render

    monkeypatch.setattr(render, "render_pdf", lambda p, l, **k: f"storage/proposals/{p.id}.pdf")

    class FakeProvider:
        def complete(self, system, user):
            return ('{"diagnostico": "d", "problemas": [], "oportunidades": [], "soluciones": [], '
                    '"beneficios": [], "tiempo_estimado": "4 semanas", "precio": 1000, "roi_estimado": "2x"}')

    monkeypatch.setattr(llm, "get_provider", lambda: FakeProvider())

    res = client.post(f"/leads/{lead.id}/proposals", headers=auth_headers)
    assert res.status_code == 202
    assert "task_id" in res.json()

    # con Celery eager, la propuesta ya quedó persistida
    latest = client.get(f"/leads/{lead.id}/proposals", headers=auth_headers).json()
    assert latest["content"]["diagnostico"] == "d"
    assert latest["price"] == 1000.0


def test_post_proposal_lead_404(client, auth_headers):
    res = client.post(f"/leads/{uuid.uuid4()}/proposals", headers=auth_headers)
    assert res.status_code == 404


def test_get_latest_proposal_null(client, auth_headers, lead):
    res = client.get(f"/leads/{lead.id}/proposals", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() is None


def test_get_latest_proposal_returns_row(client, auth_headers, lead, db):
    p = Proposal(lead_id=lead.id, content={"diagnostico": "d"}, price=1500, pdf_path=None)
    db.add(p)
    db.commit()
    db.refresh(p)
    res = client.get(f"/leads/{lead.id}/proposals", headers=auth_headers)
    body = res.json()
    assert body["content"]["diagnostico"] == "d"
    assert body["pdf_available"] is False


def test_get_pdf_404_when_missing(client, auth_headers, lead, db):
    p = Proposal(lead_id=lead.id, content={}, price=None, pdf_path=None)
    db.add(p)
    db.commit()
    db.refresh(p)
    res = client.get(f"/proposals/{p.id}/pdf", headers=auth_headers)
    assert res.status_code == 404


def test_get_pdf_serves_file(client, auth_headers, lead, db, tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    p = Proposal(lead_id=lead.id, content={}, price=None, pdf_path=str(pdf))
    db.add(p)
    db.commit()
    db.refresh(p)
    res = client.get(f"/proposals/{p.id}/pdf", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"


def test_proposals_require_auth(client, lead):
    assert client.post(f"/leads/{lead.id}/proposals").status_code == 401
