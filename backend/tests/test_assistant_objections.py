from app.services.assistant import objections


def test_parse_suggestions_json_array_with_fences():
    text = '```json\n["Opción A", "Opción B", "Opción C"]\n```'
    out = objections.parse_suggestions(text)
    assert out == ["Opción A", "Opción B", "Opción C"]


def test_parse_suggestions_json_with_surrounding_text():
    text = 'Claro:\n["Uno", "Dos"]\nEso es todo.'
    assert objections.parse_suggestions(text) == ["Uno", "Dos"]


def test_parse_suggestions_numbered_list_fallback():
    text = "1. Primera respuesta\n2. Segunda respuesta\n3. Tercera"
    assert objections.parse_suggestions(text) == ["Primera respuesta", "Segunda respuesta", "Tercera"]


def test_parse_suggestions_bullets_fallback():
    text = "- Una\n- Dos\n• Tres"
    assert objections.parse_suggestions(text) == ["Una", "Dos", "Tres"]


def test_parse_suggestions_caps_at_three():
    text = '["a", "b", "c", "d", "e"]'
    assert objections.parse_suggestions(text) == ["a", "b", "c"]


def test_parse_suggestions_empty():
    assert objections.parse_suggestions("no hay nada útil aquí...") == []
    assert objections.parse_suggestions("") == []


def test_build_prompt_includes_context():
    class L:
        business_name = "Gym X"; industry = "gym"; city = "Bogotá"

    class M:
        def __init__(self, direction, body):
            self.direction = direction; self.body = body

    msgs = [M("out", "Hola, ¿te interesa?"), M("in", "Está muy caro")]
    system, user = objections.build_prompt(L(), msgs, "precio alto")
    assert "JSON" in system
    assert "Gym X" in user
    assert "precio alto" in user
    assert "Está muy caro" in user


def test_build_prompt_without_messages_or_objection():
    class L:
        business_name = "Gym X"; industry = None; city = None

    system, user = objections.build_prompt(L(), [], None)
    assert "Gym X" in user
