"""proposals

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "proposals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("lead_id", sa.UUID(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=True),
        sa.Column("pdf_path", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_proposals_lead_id"), "proposals", ["lead_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_proposals_lead_id"), table_name="proposals")
    op.drop_table("proposals")
