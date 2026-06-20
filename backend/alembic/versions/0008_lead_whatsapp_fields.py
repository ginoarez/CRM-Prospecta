"""lead whatsapp opt-out and last inbound

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("whatsapp_opt_out", sa.Boolean(), nullable=False,
                                     server_default=sa.text("false")))
    op.add_column("leads", sa.Column("last_inbound_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("leads", "last_inbound_at")
    op.drop_column("leads", "whatsapp_opt_out")
