import types

from app.services.messaging import wa_link


def _lead(**kw):
    base = {"business_name": "Gym X", "city": "Bogota", "country": "US",
            "industry": "gimnasios", "phone": "(1) 234 567 8900"}
    base.update(kw)
    return types.SimpleNamespace(**base)


def test_render_substitutes_known_fields():
    out = wa_link.render_template("Hola {business_name} de {city} ({industry})", _lead())
    assert out == "Hola Gym X de Bogota (gimnasios)"


def test_render_null_field_becomes_empty():
    out = wa_link.render_template("Ciudad: {city}.", _lead(city=None))
    assert out == "Ciudad: ."


def test_render_unknown_placeholder_stays_literal():
    out = wa_link.render_template("Te ayudo con {beneficio}", _lead())
    assert out == "Te ayudo con {beneficio}"


def test_render_plain_text_unchanged():
    assert wa_link.render_template("sin variables", _lead()) == "sin variables"


def test_build_wa_link_valid_phone():
    result = wa_link.build_wa_link(_lead(), "hola mundo")
    assert result == {
        "url": "https://wa.me/12345678900?text=hola%20mundo",
        "body": "hola mundo",
        "phone": "12345678900",
    }


def test_build_wa_link_no_phone_returns_none():
    assert wa_link.build_wa_link(_lead(phone=None), "x") is None
    assert wa_link.build_wa_link(_lead(phone="not-a-number", country=None), "x") is None
