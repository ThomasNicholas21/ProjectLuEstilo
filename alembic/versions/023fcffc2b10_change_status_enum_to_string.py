"""change_status_enum_to_string

Revision ID: 023fcffc2b10
Revises: f9c43b705599
Create Date: 2025-05-24 22:39:14.856587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '023fcffc2b10'
down_revision: Union[str, None] = 'f9c43b705599'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
enum_name = 'orderstatus'

def upgrade():
    op.execute("ALTER TABLE \"order\" ALTER COLUMN status TYPE VARCHAR(20) USING status::text;")
    op.execute(f"DROP TYPE IF EXISTS {enum_name};")


def downgrade():
    op.execute("CREATE TYPE orderstatus AS ENUM ('pendente', 'processando', 'finalizado', 'cancelado');")
    op.execute("ALTER TABLE \"order\" ALTER COLUMN status TYPE orderstatus USING status::orderstatus;")
