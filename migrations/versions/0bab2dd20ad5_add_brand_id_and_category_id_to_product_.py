"""Add brand_id and category_id to product_def

Revision ID: 0bab2dd20ad5
Revises: a57b9d70b684
Create Date: 2020-11-14 21:01:47.283876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bab2dd20ad5'
down_revision = 'a57b9d70b684'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_tag_product_def', sa.Column('brand_id', sa.Integer(), nullable=False, comment='FK to brand table'))
    op.add_column('price_tag_product_def', sa.Column('category_id', sa.Integer(), nullable=False, comment='FK to category table'))
    op.create_foreign_key(None, 'price_tag_product_def', 'price_brand', ['brand_id'], ['id'])
    op.create_foreign_key(None, 'price_tag_product_def', 'price_category', ['category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'price_tag_product_def', type_='foreignkey')
    op.drop_constraint(None, 'price_tag_product_def', type_='foreignkey')
    op.drop_column('price_tag_product_def', 'category_id')
    op.drop_column('price_tag_product_def', 'brand_id')
    # ### end Alembic commands ###
