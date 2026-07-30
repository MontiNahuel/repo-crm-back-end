"""add_supervisor_role

Revision ID: 03100eb82c75
Revises: 733bd683c2dd
Create Date: 2026-06-01 19:40:24.159246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03100eb82c75'
down_revision: Union[str, None] = '733bd683c2dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agrega 'SUPERVISOR' a los valores permitidos del ENUM de forma nativa en MySQL
    op.execute(
        "ALTER TABLE usuarios MODIFY COLUMN rol ENUM('ADMIN', 'SUPERVISOR', 'VENDEDOR', 'CLIENTE', 'LEAD_WEB') NOT NULL DEFAULT 'LEAD_WEB';"
    )


def downgrade() -> None:
    # Revierte el ENUM a los valores originales
    # Nota: Asegúrate de reasignar a cualquier usuario 'SUPERVISOR' antes de revertir
    op.execute(
        "ALTER TABLE usuarios MODIFY COLUMN rol ENUM('ADMIN', 'VENDEDOR', 'CLIENTE', 'LEAD_WEB') NOT NULL DEFAULT 'LEAD_WEB';"
    )
