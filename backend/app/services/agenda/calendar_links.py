import urllib.parse
from datetime import datetime, timedelta, timezone


def _utc_stamp(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _end(meeting) -> datetime:
    start = meeting.scheduled_at
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return start + timedelta(minutes=meeting.duration_minutes or 0)


def google_calendar_url(meeting, lead) -> str:
    start = _utc_stamp(meeting.scheduled_at)
    end = _utc_stamp(_end(meeting))
    details = meeting.notes or ""
    if getattr(lead, "business_name", None):
        details = (details + f"\nLead: {lead.business_name}").strip()
    params = {
        "action": "TEMPLATE",
        "text": meeting.title or "",
        "dates": f"{start}/{end}",
        "details": details,
        "location": meeting.location or "",
    }
    return "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(params)


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def build_ics(meeting, lead) -> str:
    description = meeting.notes or ""
    if getattr(lead, "business_name", None):
        description = (description + f"\nLead: {lead.business_name}").strip()
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Prospecta CRM//Agenda//ES",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{meeting.id}@prospecta",
        f"DTSTAMP:{_utc_stamp(datetime.now(timezone.utc))}",
        f"DTSTART:{_utc_stamp(meeting.scheduled_at)}",
        f"DTEND:{_utc_stamp(_end(meeting))}",
        f"SUMMARY:{_esc(meeting.title)}",
        f"DESCRIPTION:{_esc(description)}",
        f"LOCATION:{_esc(meeting.location or '')}",
        f"STATUS:{'CANCELLED' if getattr(meeting, 'status', '') == 'cancelada' else 'CONFIRMED'}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(lines) + "\r\n"
