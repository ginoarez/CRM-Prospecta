import httpx
import pytest

from app.core.config import settings
from app.services.whatsapp import cloud_api


class FakeResponse:
    def __init__(self):
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {"messages": [{"id": "wamid.out"}]}


class FakeClient:
    calls = []

    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, json=None, headers=None):
        FakeClient.calls.append({"url": url, "json": json, "headers": headers})
        return FakeResponse()


@pytest.fixture(autouse=True)
def _client(monkeypatch):
    FakeClient.calls = []
    monkeypatch.setattr(httpx, "Client", FakeClient)
    monkeypatch.setattr(settings, "WHATSAPP_TOKEN", "tok")
    monkeypatch.setattr(settings, "WHATSAPP_PHONE_ID", "PID")
    monkeypatch.setattr(settings, "WHATSAPP_API_URL", "https://graph.test")
    monkeypatch.setattr(settings, "WHATSAPP_API_VERSION", "v21.0")


def test_send_text_posts_correct_body():
    cloud_api.send_text("573001112233", "Hola")
    call = FakeClient.calls[-1]
    assert call["url"] == "https://graph.test/v21.0/PID/messages"
    assert call["json"]["type"] == "text"
    assert call["json"]["text"]["body"] == "Hola"
    assert call["json"]["to"] == "573001112233"
    assert call["headers"]["Authorization"] == "Bearer tok"


def test_send_template_posts_components():
    cloud_api.send_template("573001112233", "promo", "es", ["Gym X"])
    call = FakeClient.calls[-1]
    assert call["json"]["type"] == "template"
    assert call["json"]["template"]["name"] == "promo"
    assert call["json"]["template"]["language"]["code"] == "es"
    comps = call["json"]["template"]["components"]
    assert comps[0]["parameters"][0]["text"] == "Gym X"


def test_requires_config(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_TOKEN", "")
    with pytest.raises(RuntimeError):
        cloud_api.send_text("573001112233", "Hola")
