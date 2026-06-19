import types

import pytest

from app.services.scoring import analyzer

VALID = '{"score": 80, "needs": ["web"], "urgency": "alta", "buy_probability": 70, ' \
        '"detected_problems": ["sin chat"], "opportunities": ["chatbot"], "summary": "ok"}'


def test_parse_plain_json():
    out = analyzer.parse_analysis(VALID)
    assert out["score"] == 80 and out["urgency"] == "alta"
    assert out["buy_probability"] == 70.0 and out["needs"] == ["web"]


def test_parse_with_fences():
    out = analyzer.parse_analysis("```json\n" + VALID + "\n```")
    assert out["score"] == 80


def test_parse_with_surrounding_text():
    out = analyzer.parse_analysis("Aquí tienes el análisis:\n" + VALID + "\nFin.")
    assert out["score"] == 80


def test_parse_clamps_ranges():
    out = analyzer.parse_analysis('{"score": 150, "buy_probability": -5, "urgency": "x"}')
    assert out["score"] == 100
    assert out["buy_probability"] == 0.0
    assert out["urgency"] is None  # normalizado: valor inválido -> None


def test_parse_invalid_raises():
    with pytest.raises(ValueError):
        analyzer.parse_analysis("no hay json aquí")


def test_build_prompt_includes_signals_and_lead():
    lead = types.SimpleNamespace(business_name="Gym X", industry="gym", city="BA", website="http://x")
    system, user = analyzer.build_prompt(lead, {"website_reachable": True, "has_chat_widget": False})
    assert "JSON" in system
    assert "Gym X" in user and "website_reachable" in user
