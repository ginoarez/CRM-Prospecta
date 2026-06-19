"""ai_analyses

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("lead_id", sa.UUID(), nullable=False),
        sa.Column("score", sa.SmallInteger(), nullable=True),
        sa.Column("needs", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("urgency", sa.String(), nullable=True),
        sa.Column("buy_probability", sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column("detected_problems", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("opportunities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("raw_signals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_analyses_lead_id"), "ai_analyses", ["lead_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_analyses_lead_id"), table_name="ai_analyses")
    op.drop_table("ai_analyses")
