"""order orderitem table

Revision ID: 1a422c6f39bd
Revises: 88942dee3af3
Create Date: 2025-05-24 03:11:24.072265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1a422c6f39bd'
down_revision: Union[str, None] = '88942dee3af3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('product',
    sa.Column('id_product', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('bar_code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('valid_date', sa.DateTime(), nullable=True),
    sa.Column('images', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('section', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id_product'),
    sa.UniqueConstraint('bar_code')
    )
    op.create_index(op.f('ix_product_id_product'), 'product', ['id_product'], unique=False)
    op.create_table('order',
    sa.Column('id_order', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_client', sa.Integer(), nullable=False),
    sa.Column('total_amount', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED', name='orderstatus'), nullable=True),
    sa.ForeignKeyConstraint(['id_client'], ['client.id_client'], ),
    sa.PrimaryKeyConstraint('id_order')
    )
    op.create_index(op.f('ix_order_id_order'), 'order', ['id_order'], unique=False)
    op.create_table('orderitem',
    sa.Column('id_orderitem', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id_order', sa.Integer(), nullable=False),
    sa.Column('id_product', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['id_order'], ['order.id_order'], ),
    sa.ForeignKeyConstraint(['id_product'], ['product.id_product'], ),
    sa.PrimaryKeyConstraint('id_orderitem')
    )
    op.create_index(op.f('ix_orderitem_id_orderitem'), 'orderitem', ['id_orderitem'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orderitem_id_orderitem'), table_name='orderitem')
    op.drop_table('orderitem')
    op.drop_index(op.f('ix_order_id_order'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_product_id_product'), table_name='product')
    op.drop_table('product')
