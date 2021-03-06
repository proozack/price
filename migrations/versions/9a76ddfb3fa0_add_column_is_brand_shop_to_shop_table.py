"""Add column is_brand_shop to shop table

Revision ID: 9a76ddfb3fa0
Revises: ef8661546e17
Create Date: 2020-10-11 19:45:38.379392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a76ddfb3fa0'
down_revision = 'ef8661546e17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('price_image_control_sum_idx', table_name='price_image')
    op.drop_index('price_image_image_idx', table_name='price_image')
    op.drop_index('price_ofert_image_idx', table_name='price_ofert')
    op.add_column('price_shop', sa.Column('is_brand_shop', sa.Boolean(), nullable=True, comment='Information about is a brand shop or no'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('price_shop', 'is_brand_shop')
    op.create_index('price_ofert_image_idx', 'price_ofert', ['image'], unique=False)
    op.create_index('price_image_image_idx', 'price_image', ['image'], unique=False)
    op.create_index('price_image_control_sum_idx', 'price_image', ['control_sum'], unique=False)
    # ### end Alembic commands ###
