import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models import LeadStatus


class LeadCreate(BaseModel):
    business_name: str
    industry: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    socials: dict = {}
    company_size: str | None = None
    employees: int | None = None
    notes: str | None = None
    source: str = "manual"


class LeadUpdate(BaseModel):
    business_name: str | None = None
    industry: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    socials: dict | None = None
    company_size: str | None = None
    employees: int | None = None
    notes: str | None = None


class StageUpdate(BaseModel):
    status: LeadStatus


class LeadOut(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID | None
    business_name: str
    industry: str | None
    city: str | None
    country: str | None
    phone: str | None
    email: str | None
    website: str | None
    socials: dict
    company_size: str | None
    employees: int | None
    status: LeadStatus
    score: int | None
    source: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    whatsapp_opt_out: bool
    last_inbound_at: datetime | None

    model_config = {"from_attributes": True}


class LeadList(BaseModel):
    items: list[LeadOut]
    total: int
    page: int
    page_size: int
