"""templates and messages

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("lead_id", sa.UUID(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("template_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_lead_id"), "messages", ["lead_id"], unique=False)
    op.execute(
        "INSERT INTO templates (id, name, channel, body, created_at) VALUES "
        "(gen_random_uuid(), 'Toque frío básico', 'wa', "
        "'¡Hola {business_name}! 👋 Vi que están en {city}. Trabajo con {industry} "
        "ayudándolos a crecer. ¿Te muestro cómo en 2 min?', now())"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_messages_lead_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_table("templates")
