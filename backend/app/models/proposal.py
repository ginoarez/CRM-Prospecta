import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    pdf_path: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
