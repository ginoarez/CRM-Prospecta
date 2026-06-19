import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Template, User
from app.schemas.template import TemplateCreate, TemplateOut, TemplateUpdate

router = APIRouter(prefix="/templates", tags=["templates"])


def _template_or_404(db, template_id):
    t = db.get(Template, template_id)
    if t is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="template not found")
    return t


@router.get("", response_model=list[TemplateOut])
def list_templates(channel: str | None = None, db: Session = Depends(get_db),
                   _: User = Depends(get_current_user)):
    query = db.query(Template)
    if channel:
        query = query.filter(Template.channel == channel)
    return query.order_by(Template.created_at.desc()).all()


@router.post("", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
def create_template(body: TemplateCreate, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    t = Template(**body.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.patch("/{template_id}", response_model=TemplateOut)
def update_template(template_id: uuid.UUID, body: TemplateUpdate, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    t = _template_or_404(db, template_id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(t, key, value)
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: uuid.UUID, db: Session = Depends(get_db),
                    _: User = Depends(get_current_user)):
    t = _template_or_404(db, template_id)
    db.delete(t)
    db.commit()
