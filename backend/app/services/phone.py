import phonenumbers


def normalize_phone(raw: str | None, country: str | None) -> str | None:
    if not raw or not raw.strip():
        return None
    region = country.strip().upper() if country else None
    try:
        parsed = phonenumbers.parse(raw, region)
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
