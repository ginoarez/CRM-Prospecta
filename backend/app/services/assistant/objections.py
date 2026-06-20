import json
import re

_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)
_LEAD_MARK = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s*")


def build_prompt(lead, messages, objection: str | None) -> tuple[str, str]:
    system = (
        "Eres un asesor de ventas consultivo de una agencia de IA, automatización, desarrollo web y "
        "marketing. Propón de 2 a 3 respuestas BREVES, empáticas y orientadas a valor que UN HUMANO "
        "podría enviar por WhatsApp para manejar la objeción del prospecto. Responde SOLO con un array "
        "JSON de strings en español, sin texto alrededor. No inventes datos ni precios; nunca te hagas "
        "pasar por el cliente."
    )
    lines = [
        f"Negocio: {lead.business_name}",
        f"Industria: {lead.industry or 'desconocida'}",
        f"Ciudad: {lead.city or 'desconocida'}",
    ]
    if objection:
        lines.append(f"Objeción del prospecto: {objection}")
    if messages:
        lines.append("Conversación reciente:")
        for m in messages:
            who = "Prospecto" if getattr(m, "direction", "out") == "in" else "Nosotros"
            lines.append(f"[{who}] {m.body or ''}")
    else:
        lines.append("(sin conversación previa registrada)")
    return system, "\n".join(lines)


def _from_json_array(text: str) -> list[str] | None:
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    return [str(x).strip() for x in data if str(x).strip()]


def parse_suggestions(text: str) -> list[str]:
    cleaned = _FENCE.sub("", text or "").replace("```", "").strip()
    items = _from_json_array(cleaned)
    if items is None:
        items = []
        for line in cleaned.splitlines():
            if _LEAD_MARK.match(line):
                stripped = _LEAD_MARK.sub("", line).strip()
                if stripped:
                    items.append(stripped)
    return items[:3]
