import anthropic


class AnthropicProvider:
    def __init__(self, api_key: str, model: str):
        self._client = anthropic.Anthropic(api_key=api_key or "missing")
        self._model = model

    def complete(self, system: str, user: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in resp.content if getattr(block, "type", None) == "text"
        )
