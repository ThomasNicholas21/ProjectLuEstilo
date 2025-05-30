"""user table

Revision ID: a43044b0f226
Revises: b8e4d89a9499
Create Date: 2025-05-24 03:14:58.920343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a43044b0f226'
down_revision: Union[str, None] = 'b8e4d89a9499'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
    sa.Column('id_user', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'STAFF', name='userrole'), nullable=False),
    sa.PrimaryKeyConstraint('id_user'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_id_user'), 'user', ['id_user'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_id_user'), table_name='user')
    op.drop_table('user')
