from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas.geo import CategoryOut
from app.services.geo import categories

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/categories", response_model=list[CategoryOut])
def get_categories(_: User = Depends(get_current_user)):
    return categories.list_categories()
