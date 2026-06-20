from app.services.messaging.email_compose import render_email


class _Lead:
    business_name = "Gym X"; city = "Bogotá"; industry = "gym"; country = "CO"


class _Tpl:
    def __init__(self, subject, body):
        self.subject = subject
        self.body = body


def test_render_email_substitutes_subject_and_body():
    subject, body = render_email(_Tpl("Idea para {business_name}", "Hola {business_name} en {city}"), _Lead())
    assert subject == "Idea para Gym X"
    assert body == "Hola Gym X en Bogotá"


def test_render_email_unknown_placeholder_literal():
    subject, body = render_email(_Tpl("{business_name}", "Hola {desconocido}"), _Lead())
    assert body == "Hola {desconocido}"


def test_render_email_without_subject_is_empty():
    subject, body = render_email(_Tpl(None, "cuerpo"), _Lead())
    assert subject == ""
    assert body == "cuerpo"
