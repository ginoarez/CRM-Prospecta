import pytest

from app.core.config import settings
from app.services import llm
from app.services.llm.anthropic_provider import AnthropicProvider


def test_get_provider_anthropic(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test-key")
    provider = llm.get_provider()
    assert isinstance(provider, AnthropicProvider)


@pytest.mark.parametrize("name", ["openai", "gemini", "unknown"])
def test_get_provider_unimplemented(monkeypatch, name):
    monkeypatch.setattr(settings, "LLM_PROVIDER", name)
    with pytest.raises(NotImplementedError):
        llm.get_provider()


def test_anthropic_complete_returns_text(monkeypatch):
    provider = AnthropicProvider(api_key="test-key", model="claude-opus-4-8")

    class FakeBlock:
        type = "text"
        text = "hello"

    class FakeMessages:
        def create(self, **kwargs):
            class R: content = [FakeBlock()]
            return R()

    provider._client.messages = FakeMessages()
    assert provider.complete("sys", "usr") == "hello"
