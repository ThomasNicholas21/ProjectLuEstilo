"""client table

Revision ID: 0aee2a570ade
Revises: 
Create Date: 2025-05-23 00:54:52.727760

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0aee2a570ade'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('client',
    sa.Column('id_client', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('cpf', sa.String(length=14), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id_client')
    )
    op.create_index(op.f('ix_client_cpf'), 'client', ['cpf'], unique=True)
    op.create_index(op.f('ix_client_email'), 'client', ['email'], unique=True)
    op.create_index(op.f('ix_client_id_client'), 'client', ['id_client'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_client_id_client'), table_name='client')
    op.drop_index(op.f('ix_client_email'), table_name='client')
    op.drop_index(op.f('ix_client_cpf'), table_name='client')
    op.drop_table('client')
