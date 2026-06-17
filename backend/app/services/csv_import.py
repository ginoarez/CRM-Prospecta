import csv
import io
import uuid

from sqlalchemy.orm import Session

from app.models import Lead
from app.services.phone import normalize_phone

KNOWN_COLUMNS = {
    "business_name", "industry", "city", "country", "phone",
    "email", "website", "company_size", "employees", "notes",
}


def import_csv(db: Session, raw: bytes, owner_id: uuid.UUID) -> dict:
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    errors: list[dict] = []
    for i, row in enumerate(reader, start=1):
        data = {k: (v.strip() if isinstance(v, str) else v)
                for k, v in row.items() if k in KNOWN_COLUMNS and v not in (None, "")}
        if not data.get("business_name"):
            errors.append({"row": i, "error": "business_name is required"})
            continue
        if data.get("employees"):
            try:
                data["employees"] = int(data["employees"])
            except ValueError:
                data.pop("employees")
        if data.get("phone"):
            data["phone"] = normalize_phone(data["phone"], data.get("country"))
        db.add(Lead(owner_id=owner_id, source="csv", **data))
        created += 1
    db.commit()
    return {"created": created, "errors": errors}
