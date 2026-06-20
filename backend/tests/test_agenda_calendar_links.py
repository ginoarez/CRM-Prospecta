import uuid
from datetime import datetime, timezone

from app.services.agenda import calendar_links as cl


class _Meeting:
    id = uuid.uuid4()
    title = "Demo, parte 1"
    scheduled_at = datetime(2026, 6, 25, 15, 0, 0, tzinfo=timezone.utc)
    duration_minutes = 30
    location = "Google Meet"
    notes = "Mostrar propuesta"
    status = "programada"


class _Lead:
    business_name = "Gym X"


def test_utc_stamp_aware_and_naive():
    aware = datetime(2026, 6, 25, 15, 0, 0, tzinfo=timezone.utc)
    naive = datetime(2026, 6, 25, 15, 0, 0)
    assert cl._utc_stamp(aware) == "20260625T150000Z"
    assert cl._utc_stamp(naive) == "20260625T150000Z"


def test_google_calendar_url_has_text_and_dates():
    url = cl.google_calendar_url(_Meeting(), _Lead())
    assert url.startswith("https://calendar.google.com/calendar/render?action=TEMPLATE")
    assert "dates=20260625T150000Z%2F20260625T153000Z" in url  # start/end, +30min, '/' encoded
    assert "Demo" in url  # title presente (codificado)
    assert "Gym" in url   # business_name en details


def test_build_ics_structure_and_escaping():
    ics = cl.build_ics(_Meeting(), _Lead())
    assert "BEGIN:VCALENDAR" in ics and "END:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics and "END:VEVENT" in ics
    assert "DTSTART:20260625T150000Z" in ics
    assert "DTEND:20260625T153000Z" in ics
    assert "SUMMARY:Demo\\, parte 1" in ics  # coma escapada
    assert "LOCATION:Google Meet" in ics
    assert ics.endswith("\r\n")
