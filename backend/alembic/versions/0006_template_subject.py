"""template subject column for email

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("templates", sa.Column("subject", sa.Text(), nullable=True))
    op.execute(
        "INSERT INTO templates (id, name, channel, subject, body, created_at) VALUES "
        "(gen_random_uuid(), 'Presentación por email', 'email', "
        "'Una idea para {business_name}', "
        "'Hola {business_name},\n\nVi que trabajan en {industry} en {city} y quería compartirles "
        "una idea para conseguir más clientes con automatización e IA. ¿Tienen 15 min esta semana?\n\n"
        "Saludos.', now())"
    )


def downgrade() -> None:
    op.drop_column("templates", "subject")
