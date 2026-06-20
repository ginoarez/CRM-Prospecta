import uuid

from app.services.proposals import render


def _proposal():
    class P:
        id = uuid.uuid4()
        price = 2500.0
        content = {
            "diagnostico": "Necesitan presencia digital",
            "problemas": ["sin web"], "oportunidades": ["captar leads"],
            "soluciones": ["sitio web", "chatbot"], "beneficios": ["más ventas"],
            "tiempo_estimado": "4-6 semanas", "precio": 2500, "roi_estimado": "3x",
        }
    return P()


def _lead():
    class L:
        business_name = "Gym X"; city = "Bogotá"; industry = "gym"
    return L()


def test_render_html_contains_business_and_branding():
    html = render.render_html(_proposal(), _lead())
    assert "Gym X" in html
    assert "Necesitan presencia digital" in html
    assert "sitio web" in html
    # branding por defecto desde settings
    assert "Tu Agencia" in html


def test_render_html_lists_soluciones():
    html = render.render_html(_proposal(), _lead())
    assert "chatbot" in html
