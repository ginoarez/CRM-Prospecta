from app.core import security


def test_password_hash_roundtrip():
    h = security.hash_password("secret123")
    assert h != "secret123"
    assert security.verify_password("secret123", h) is True
    assert security.verify_password("wrong", h) is False


def test_jwt_roundtrip():
    token = security.create_access_token(subject="user-id-1")
    assert security.decode_token(token)["sub"] == "user-id-1"


def test_refresh_token_has_type():
    token = security.create_refresh_token(subject="user-id-1")
    payload = security.decode_token(token)
    assert payload["type"] == "refresh"
    assert payload["sub"] == "user-id-1"
