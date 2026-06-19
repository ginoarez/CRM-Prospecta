import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

_UA = "ProspectaCRM/1.0 (+scoring)"
_CHAT = ["intercom", "tawk", "crisp", "drift", "zendesk", "livechat"]
_BOOKING = ["calendly", "booking", "reserva", "appointment", "acuity"]
_SOCIALS = {
    "instagram": "instagram.com",
    "facebook": "facebook.com",
    "linkedin": "linkedin.com",
    "twitter": "twitter.com",
    "tiktok": "tiktok.com",
}


def _normalize(website: str) -> str:
    return website if website.startswith("http") else f"https://{website}"


def fetch_html(website: str | None) -> str | None:
    if not website:
        return None
    try:
        resp = httpx.get(
            _normalize(website),
            timeout=settings.SCRAPE_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": _UA},
        )
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def parse_signals(html: str, website: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    low = html.lower()
    return {
        "website_reachable": True,
        "https": website.startswith("https"),
        "has_viewport_meta": soup.find("meta", attrs={"name": "viewport"}) is not None,
        "has_chat_widget": any(c in low for c in _CHAT),
        "has_booking": any(b in low for b in _BOOKING),
        "social_links": sorted({k for k, dom in _SOCIALS.items() if dom in low}),
    }


def collect_signals(website: str | None) -> dict:
    html = fetch_html(website)
    if html is None:
        return {"website_reachable": False}
    return parse_signals(html, _normalize(website))
