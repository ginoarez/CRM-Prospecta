import httpx

from app.core.config import settings


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
        })
    return out


def fetch_pois(bbox: list[float], tags: list[tuple[str, str]]) -> list[dict]:
    resp = httpx.post(
        settings.OVERPASS_URL,
        data={"data": build_query(bbox, tags)},
        timeout=settings.GEO_HTTP_TIMEOUT,
    )
    resp.raise_for_status()
    return parse_elements(resp.json().get("elements", []))
