import json
import re

_FENCE = re.compile(r"```(?:json)?", re.IGNORECASE)


def build_prompt(lead, signals: dict) -> tuple[str, str]:
    system = (
        "Eres un analista de ventas para una agencia de IA, automatización, desarrollo web y "
        "marketing. Analiza el negocio y responde SOLO con un objeto JSON válido (sin texto "
        "alrededor) con estas claves exactas: score (entero 0-100), needs (lista de entre "
        "automatizacion, chatbot, web, crm, ads), urgency (baja|media|alta), buy_probability "
        "(número 0-100), detected_problems (lista de strings), opportunities (lista de strings), "
        "summary (2-3 frases en español)."
    )
    user = (
        f"Negocio: {lead.business_name}\n"
        f"Categoría: {lead.industry or 'desconocida'}\n"
        f"Ciudad: {lead.city or 'desconocida'}\n"
        f"Web: {lead.website or 'ninguna'}\n"
        f"Señales del sitio: {json.dumps(signals, ensure_ascii=False)}"
    )
    return system, user


def _clamp(value, lo: float = 0, hi: float = 100):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, n))


def parse_analysis(text: str) -> dict:
    cleaned = _FENCE.sub("", text).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in LLM output")
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in LLM output: {exc}") from exc

    score = _clamp(data.get("score"))
    buy = _clamp(data.get("buy_probability"))
    urgency = data.get("urgency")
    if urgency not in ("baja", "media", "alta"):
        urgency = None
    return {
        "score": int(score) if score is not None else None,
        "needs": data.get("needs") or [],
        "urgency": urgency,
        "buy_probability": round(buy, 1) if buy is not None else None,
        "detected_problems": data.get("detected_problems") or [],
        "opportunities": data.get("opportunities") or [],
        "summary": data.get("summary"),
    }
