from app.services.phone import normalize_phone


def test_normalizes_local_number_with_country():
    assert normalize_phone("(55) 1234 5678", "MX") == "+525512345678"


def test_passes_through_e164():
    assert normalize_phone("+525512345678", None) == "+525512345678"


def test_returns_none_for_garbage():
    assert normalize_phone("not a phone", "MX") is None


def test_returns_none_when_empty():
    assert normalize_phone("", "MX") is None
    assert normalize_phone(None, "MX") is None


def test_returns_none_without_region_for_local():
    # local number, no country to infer region -> cannot parse
    assert normalize_phone("5512345678", None) is None
