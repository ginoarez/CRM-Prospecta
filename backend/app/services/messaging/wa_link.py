import re
import urllib.parse

from app.services.phone import normalize_phone

_KNOWN = ("business_name", "city", "country", "industry")
_VAR = re.compile(r"\{(\w+)\}")


def render_template(body: str, lead) -> str:
    def repl(match: re.Match) -> str:
        key = match.group(1)
        if key in _KNOWN:
            return getattr(lead, key, None) or ""
        return match.group(0)  # placeholder desconocido: se deja literal

    return _VAR.sub(repl, body)


def build_wa_link(lead, body: str) -> dict | None:
    e164 = normalize_phone(lead.phone, lead.country)
    if e164 is None:
        return None
    digits = e164.lstrip("+")
    url = f"https://wa.me/{digits}?text={urllib.parse.quote(body)}"
    return {"url": url, "body": body, "phone": digits}
