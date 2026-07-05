from pydantic import BaseModel


class CategoryOut(BaseModel):
    key: str
    label: str


class SearchRequest(BaseModel):
    location: str
    category: str


class GeoDetails(BaseModel):
    category: str | None = None
    opening_hours: str | None = None
    brand: str | None = None
    email: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    wheelchair: str | None = None
    delivery: bool | None = None
    takeaway: bool | None = None


class GeoResult(BaseModel):
    osm_id: str
    name: str
    lat: float
    lng: float
    website: str | None = None
    phone: str | None = None
    address: str | None = None
    details: GeoDetails = GeoDetails()
    google_maps_url: str = ""
    already_imported: bool = False


class SearchResponse(BaseModel):
    location: str
    category: str
    bbox: list[float]
    count: int
    results: list[GeoResult]


class ImportItem(BaseModel):
    osm_id: str
    name: str
    lat: float | None = None
    lng: float | None = None
    website: str | None = None
    phone: str | None = None
    address: str | None = None
    category: str | None = None


class ImportRequest(BaseModel):
    items: list[ImportItem]


class ImportResponse(BaseModel):
    created: int
    skipped_existing: int
