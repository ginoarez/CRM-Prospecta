import httpx

from app.core.config import settings

_USER_AGENT = "ProspectaCRM/0.1 (ginoarez23@gmail.com)"


def geocode(location: str) -> list[float] | None:
    """Devuelve el bbox [south, north, west, east] del lugar, o None si no existe."""
    resp = httpx.get(
        f"{settings.NOMINATIM_URL}/search",
        params={"q": location, "format": "json", "limit": 1},
        headers={"User-Agent": _USER_AGENT},
        timeout=settings.GEO_HTTP_TIMEOUT,
        verify=settings.OUTBOUND_SSL_VERIFY,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data:
        return None
    bb = data[0]["boundingbox"]  # ["south", "north", "west", "east"] (strings)
    return [float(bb[0]), float(bb[1]), float(bb[2]), float(bb[3])]
