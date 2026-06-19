from app.services import llm
import app.services.scoring.signals as sig
from app.api.routers.tasks import map_celery_state

VALID = '{"score": 77, "needs": ["chatbot"], "urgency": "media", "buy_probability": 60, ' \
        '"detected_problems": ["x"], "opportunities": ["y"], "summary": "ok"}'


class FakeProvider:
    def complete(self, system, user):
        return VALID


def _patch_llm(monkeypatch):
    monkeypatch.setattr(sig, "fetch_html", lambda w: None)
    monkeypatch.setattr(llm, "get_provider", lambda: FakeProvider())


def test_map_celery_state():
    assert map_celery_state("PENDING") == "pending"
    assert map_celery_state("STARTED") == "running"
    assert map_celery_state("SUCCESS") == "success"
    assert map_celery_state("FAILURE") == "failure"
    assert map_celery_state("WHATEVER") == "pending"


def test_analyze_creates_analysis(client, auth_headers, monkeypatch):
    _patch_llm(monkeypatch)
    lead_id = client.post("/leads", json={"business_name": "X"}, headers=auth_headers).json()["id"]
    r = client.post(f"/leads/{lead_id}/analyze", headers=auth_headers)
    assert r.status_code == 202
    assert r.json()["task_id"]
    a = client.get(f"/leads/{lead_id}/analysis", headers=auth_headers)
    assert a.status_code == 200
    assert a.json()["score"] == 77


def test_analysis_null_when_never_analyzed(client, auth_headers):
    lead_id = client.post("/leads", json={"business_name": "Y"}, headers=auth_headers).json()["id"]
    r = client.get(f"/leads/{lead_id}/analysis", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() is None


def test_analyze_404_missing_lead(client, auth_headers):
    import uuid
    r = client.post(f"/leads/{uuid.uuid4()}/analyze", headers=auth_headers)
    assert r.status_code == 404


def test_task_status_shape(client, auth_headers):
    r = client.get("/tasks/unknown-task-id", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


def test_analyze_requires_auth(client):
    import uuid
    assert client.post(f"/leads/{uuid.uuid4()}/analyze").status_code == 401
