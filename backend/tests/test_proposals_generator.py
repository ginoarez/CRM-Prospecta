import pytest

from app.services.proposals import generator


def test_parse_proposal_with_fences():
    text = '```json\n{"diagnostico": "d", "problemas": ["p"], "oportunidades": ["o"], ' \
           '"soluciones": ["s"], "beneficios": ["b"], "tiempo_estimado": "4 semanas", ' \
           '"precio": 2500, "roi_estimado": "3x"}\n```'
    out = generator.parse_proposal(text)
    assert out["diagnostico"] == "d"
    assert out["problemas"] == ["p"]
    assert out["precio"] == 2500.0
    assert out["roi_estimado"] == "3x"


def test_parse_proposal_with_surrounding_text():
    text = 'Aquí tienes:\n{"diagnostico": "x", "precio": "$2.500"}\nGracias'
    out = generator.parse_proposal(text)
    assert out["diagnostico"] == "x"
    assert out["precio"] == 2500.0
    assert out["problemas"] == []  # listas faltantes -> []


def test_parse_proposal_price_null_when_missing():
    out = generator.parse_proposal('{"diagnostico": "x"}')
    assert out["precio"] is None


def test_parse_proposal_invalid_raises():
    with pytest.raises(ValueError):
        generator.parse_proposal("no hay json aquí")


def test_build_prompt_includes_analysis_when_present():
    class L:
        business_name = "Gym X"; industry = "gym"; city = "Bogotá"; website = "http://x.co"

    class A:
        summary = "necesita web"; needs = ["web"]; detected_problems = ["sin chatbot"]
        opportunities = ["ads"]

    system, user = generator.build_prompt(L(), A())
    assert "JSON" in system
    assert "Gym X" in user
    assert "necesita web" in user


def test_build_prompt_without_analysis():
    class L:
        business_name = "Gym X"; industry = None; city = None; website = None

    system, user = generator.build_prompt(L(), None)
    assert "Gym X" in user
    assert "sin análisis" in user.lower()
