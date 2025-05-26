"""user table

Revision ID: b8e4d89a9499
Revises: cd9897e5f369
Create Date: 2025-05-24 03:12:46.281884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e4d89a9499'
down_revision: Union[str, None] = 'cd9897e5f369'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
