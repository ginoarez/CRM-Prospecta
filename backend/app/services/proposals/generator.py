import json
import re

_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)
_NUM = re.compile(r"-?\d+(?:[.,]\d+)*")

_LIST_KEYS = ("problemas", "oportunidades", "soluciones", "beneficios")


def build_prompt(lead, analysis) -> tuple[str, str]:
    system = (
        "Eres un consultor comercial de una agencia de IA, automatización, desarrollo web y "
        "marketing. A partir del negocio y su análisis, redacta una propuesta comercial y responde "
        "SOLO con un objeto JSON válido (sin texto alrededor) con estas claves exactas: "
        "diagnostico (string, 2-3 frases), problemas (lista de strings), oportunidades (lista de "
        "strings), soluciones (lista de strings con los servicios recomendados), beneficios (lista "
        "de strings), tiempo_estimado (string, p.ej. '4-6 semanas'), precio (número en USD), "
        "roi_estimado (string). Todo en español."
    )
    lines = [
        f"Negocio: {lead.business_name}",
        f"Industria: {lead.industry or 'desconocida'}",
        f"Ciudad: {lead.city or 'desconocida'}",
        f"Web: {lead.website or 'ninguna'}",
    ]
    if analysis is not None:
        lines.append(f"Resumen del análisis: {getattr(analysis, 'summary', None) or 'n/d'}")
        lines.append(f"Necesidades: {', '.join(getattr(analysis, 'needs', None) or []) or 'n/d'}")
        lines.append(
            f"Problemas detectados: {', '.join(getattr(analysis, 'detected_problems', None) or []) or 'n/d'}")
        lines.append(
            f"Oportunidades: {', '.join(getattr(analysis, 'opportunities', None) or []) or 'n/d'}")
    else:
        lines.append("No hay análisis previo (sin análisis); propón con base en el rubro y la ciudad.")
    return system, "\n".join(lines)


def _to_price(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    m = _NUM.search(str(value))
    if not m:
        return None
    raw = m.group(0).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_proposal(text: str) -> dict:
    cleaned = _FENCE.sub("", text).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in LLM output")
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in LLM output: {exc}") from exc

    out = {
        "diagnostico": data.get("diagnostico"),
        "tiempo_estimado": data.get("tiempo_estimado"),
        "roi_estimado": data.get("roi_estimado"),
        "precio": _to_price(data.get("precio")),
    }
    for k in _LIST_KEYS:
        v = data.get(k)
        out[k] = v if isinstance(v, list) else []
    return out
