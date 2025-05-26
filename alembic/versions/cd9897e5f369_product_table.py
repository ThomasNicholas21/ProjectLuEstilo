"""product table

Revision ID: cd9897e5f369
Revises: 1a422c6f39bd
Create Date: 2025-05-24 03:12:12.604953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cd9897e5f369'
down_revision: Union[str, None] = '1a422c6f39bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
