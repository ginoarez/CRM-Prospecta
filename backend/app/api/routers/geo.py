from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Lead, User
from app.models.geo_search import GeoSearch
from app.schemas.geo import CategoryOut, GeoResult, SearchRequest, SearchResponse
from app.services.geo import categories, nominatim, overpass

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(_: User = Depends(get_current_user)):
    return categories.list_categories()


def _existing_osm_ids(db: Session) -> set[str]:
    rows = db.query(Lead.osm_id).filter(Lead.osm_id.isnot(None)).all()
    return {osm_id for (osm_id,) in rows}


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    tags = categories.get_tags(body.category)
    if tags is None:
        raise HTTPException(status_code=422, detail="unknown category")

    location_norm = body.location.strip().lower()
    cached = (
        db.query(GeoSearch)
        .filter(GeoSearch.location_text == location_norm)
        .order_by(GeoSearch.created_at.desc())
        .first()
    )
    if cached is not None:
        bbox = cached.bbox
    else:
        try:
            bbox = nominatim.geocode(body.location)
        except Exception:
            raise HTTPException(status_code=502, detail="geocoding service error")
        if bbox is None:
            raise HTTPException(status_code=404, detail="location not found")

    try:
        pois = overpass.fetch_pois(bbox, tags)
    except Exception:
        raise HTTPException(status_code=502, detail="overpass service error")

    existing = _existing_osm_ids(db)
    results = [GeoResult(**poi, already_imported=poi["osm_id"] in existing) for poi in pois]

    db.add(GeoSearch(user_id=user.id, location_text=location_norm, category=body.category,
                     bbox=bbox, result_count=len(results)))
    db.commit()

    return SearchResponse(location=body.location, category=body.category, bbox=bbox,
                          count=len(results), results=results)
