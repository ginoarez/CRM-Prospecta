import httpx

from app.core.config import settings


def _require_config() -> None:
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
        raise RuntimeError("WhatsApp Cloud API no configurada (WHATSAPP_TOKEN/PHONE_ID)")


def _post(body: dict) -> dict:
    _require_config()
    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        return resp.json()


def send_text(to: str, text: str) -> dict:
    return _post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    })


def send_template(to: str, name: str, language: str, params: list[str] | None = None) -> dict:
    template = {"name": name, "language": {"code": language}}
    if params:
        template["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in params],
        }]
    return _post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": template,
    })
