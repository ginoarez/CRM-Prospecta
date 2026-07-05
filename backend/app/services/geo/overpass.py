import httpx
from urllib.parse import quote

from app.core.config import settings

_USER_AGENT = "ProspectaCRM/0.1 (ginoarez23@gmail.com)"


def build_query(bbox: list[float], tags: list[tuple[str, str]]) -> str:
    south, north, west, east = bbox
    area = f"{south},{west},{north},{east}"
    parts = []
    for key, value in tags:
        parts.append(f'node["{key}"="{value}"]({area});')
        parts.append(f'way["{key}"="{value}"]({area});')
    return f"[out:json][timeout:25];({''.join(parts)});out center tags;"


def _address(tags: dict) -> str | None:
    parts = [tags.get("addr:street"), tags.get("addr:housenumber"), tags.get("addr:city")]
    parts = [p for p in parts if p]
    return ", ".join(parts) if parts else None


def _bool_tag(tags: dict, key: str) -> bool | None:
    v = tags.get(key)
    return None if v is None else v == "yes"


def _details(tags: dict) -> dict:
    return {
        "category": tags.get("cuisine") or tags.get("shop") or tags.get("amenity") or tags.get("leisure"),
        "opening_hours": tags.get("opening_hours"),
        "brand": tags.get("brand"),
        "email": tags.get("email") or tags.get("contact:email"),
        "instagram": tags.get("contact:instagram"),
        "facebook": tags.get("contact:facebook"),
        "wheelchair": tags.get("wheelchair"),
        "delivery": _bool_tag(tags, "delivery"),
        "takeaway": _bool_tag(tags, "takeaway"),
    }


def google_maps_url(name: str, lat: float, lng: float) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(f'{name} {lat},{lng}')}"


def parse_elements(elements: list[dict]) -> list[dict]:
    out: list[dict] = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        if el.get("type") == "node":
            lat, lng = el.get("lat"), el.get("lon")
        else:
            center = el.get("center") or {}
            lat, lng = center.get("lat"), center.get("lon")
        if lat is None or lng is None:
            continue
        out.append({
            "osm_id": f'{el["type"]}/{el["id"]}',
            "name": name,
            "lat": lat,
            "lng": lng,
            "website": tags.get("website") or tags.get("contact:website"),
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "address": _address(tags),
            "details": _details(tags),
            "google_maps_url": google_maps_url(name, lat, lng),
        })
    return out


def fetch_pois(bbox: list[float], tags: list[tuple[str, str]]) -> list[dict]:
    resp = httpx.post(
        settings.OVERPASS_URL,
        data={"data": build_query(bbox, tags)},
        headers={"User-Agent": _USER_AGENT},
        timeout=settings.GEO_HTTP_TIMEOUT,
        verify=settings.OUTBOUND_SSL_VERIFY,
    )
    resp.raise_for_status()
    return parse_elements(resp.json().get("elements", []))
