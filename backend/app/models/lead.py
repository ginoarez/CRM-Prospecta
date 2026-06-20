import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Double, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    nuevo = "nuevo"
    calificado = "calificado"
    contactado = "contactado"
    en_conversacion = "en_conversacion"
    propuesta_enviada = "propuesta_enviada"
    negociacion = "negociacion"
    ganado = "ganado"
    perdido = "perdido"
    descartado = "descartado"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    business_name: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[str | None] = mapped_column(String)
    city: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    socials: Mapped[dict] = mapped_column(JSONB, default=dict)
    company_size: Mapped[str | None] = mapped_column(String)
    employees: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.nuevo, index=True
    )
    score: Mapped[int | None] = mapped_column(SmallInteger, index=True)
    latitude: Mapped[float | None] = mapped_column(Double)
    longitude: Mapped[float | None] = mapped_column(Double)
    osm_id: Mapped[str | None] = mapped_column(String, unique=True)
    source: Mapped[str] = mapped_column(String, default="manual")
    notes: Mapped[str | None] = mapped_column(Text)
    whatsapp_opt_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_inbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
