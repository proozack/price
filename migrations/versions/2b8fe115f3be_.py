"""empty message

Revision ID: 2b8fe115f3be
Revises: 9409af8e7a50
Create Date: 2021-10-15 09:28:14.190735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b8fe115f3be'
down_revision = '9409af8e7a50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('imp_product_price_imp_catalog_page_id_idx', 'imp_product_price', ['imp_catalog_page_id'], unique=False)
    op.drop_index('price_image_image_idx', table_name='price_image')
    op.drop_index('price_ofert_image_idx', table_name='price_ofert')
    op.drop_index('price_ofert_url_idx', table_name='price_ofert')
    op.drop_index('price_tag_ofert_tag_product_def_id_idx', table_name='price_tag_ofert')
    op.drop_index('price_tag_product_tag_id_idx', table_name='price_tag_product')
    op.drop_index('price_tag_product_def_category_id_idx', table_name='price_tag_product_def')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('price_tag_product_def_category_id_idx', 'price_tag_product_def', ['category_id'], unique=False)
    op.create_index('price_tag_product_tag_id_idx', 'price_tag_product', ['tag_id'], unique=False)
    op.create_index('price_tag_ofert_tag_product_def_id_idx', 'price_tag_ofert', ['tag_product_def_id'], unique=False)
    op.create_index('price_ofert_url_idx', 'price_ofert', ['url'], unique=False)
    op.create_index('price_ofert_image_idx', 'price_ofert', ['image'], unique=False)
    op.create_index('price_image_image_idx', 'price_image', ['image'], unique=False)
    op.drop_index('imp_product_price_imp_catalog_page_id_idx', table_name='imp_product_price')
    # ### end Alembic commands ###
