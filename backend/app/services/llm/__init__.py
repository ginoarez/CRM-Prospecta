from typing import Protocol

from app.core.config import settings
from app.services.llm.anthropic_provider import AnthropicProvider


class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str: ...


def get_provider() -> LLMProvider:
    provider = settings.LLM_PROVIDER
    if provider == "anthropic":
        return AnthropicProvider(api_key=settings.ANTHROPIC_API_KEY, model=settings.LLM_MODEL)
    raise NotImplementedError(f"LLM provider '{provider}' not implemented")
