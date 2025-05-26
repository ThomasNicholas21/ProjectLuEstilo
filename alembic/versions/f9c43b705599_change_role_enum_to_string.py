"""change_role_enum_to_string

Revision ID: f9c43b705599
Revises: a43044b0f226
Create Date: 2025-05-24 16:20:25.012536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'f9c43b705599'
down_revision: Union[str, None] = 'a43044b0f226'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE "user" ALTER COLUMN role TYPE VARCHAR(20) USING role::text;')
    op.execute('DROP TYPE IF EXISTS userrole;')


def downgrade() -> None:
    op.execute("CREATE TYPE userrole AS ENUM ('ADMIN', 'STAFF');")
    op.execute('ALTER TABLE "user" ALTER COLUMN role TYPE userrole USING role::userrole;')
