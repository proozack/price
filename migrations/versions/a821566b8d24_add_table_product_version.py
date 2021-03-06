"""add table product_version

Revision ID: a821566b8d24
Revises: f7f0fa47710a
Create Date: 2020-10-24 17:12:56.621753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a821566b8d24'
down_revision = 'f7f0fa47710a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_product_image', sa.Column('product_version_id', sa.Integer(), nullable=False, comment='FK to product table'))
    op.drop_constraint('price_product_image_product_id_fkey', 'price_product_image', type_='foreignkey')
    op.create_foreign_key(None, 'price_product_image', 'price_product_version', ['product_version_id'], ['id'])
    op.drop_column('price_product_image', 'product_id')
    op.add_column('price_product_price', sa.Column('product_version_id', sa.Integer(), nullable=False, comment='FK to product table'))
    op.drop_constraint('uniq_product_id_shop_id_date_price', 'price_product_price', type_='unique')
    op.create_unique_constraint('uniq_product_id_shop_id_date_price', 'price_product_price', ['product_version_id', 'shop_id', 'date_price'])
    op.drop_constraint('price_product_price_product_id_fkey', 'price_product_price', type_='foreignkey')
    op.create_foreign_key(None, 'price_product_price', 'price_product_version', ['product_version_id'], ['id'])
    op.drop_column('price_product_price', 'product_id')
    op.add_column('price_product_shop_url', sa.Column('product_version_id', sa.Integer(), nullable=False, comment='FK to product table'))
    op.drop_constraint('uniq_product_id_shop_id_url', 'price_product_shop_url', type_='unique')
    op.create_unique_constraint('uniq_product_id_shop_id_url', 'price_product_shop_url', ['product_version_id', 'shop_id', 'url'])
    op.drop_constraint('price_product_shop_url_product_id_fkey', 'price_product_shop_url', type_='foreignkey')
    op.create_foreign_key(None, 'price_product_shop_url', 'price_product_version', ['product_version_id'], ['id'])
    op.drop_column('price_product_shop_url', 'product_id')
    op.add_column('price_tag_word_link', sa.Column('product_version_id', sa.Integer(), nullable=False, comment='FK to product table'))
    op.drop_constraint('price_tag_word_link_product_id_fkey', 'price_tag_word_link', type_='foreignkey')
    op.create_foreign_key(None, 'price_tag_word_link', 'price_product_version', ['product_version_id'], ['id'])
    op.drop_column('price_tag_word_link', 'product_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_tag_word_link', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to price_product table'))
    op.drop_constraint(None, 'price_tag_word_link', type_='foreignkey')
    op.create_foreign_key('price_tag_word_link_product_id_fkey', 'price_tag_word_link', 'price_product', ['product_id'], ['id'])
    op.drop_column('price_tag_word_link', 'product_version_id')
    op.add_column('price_product_shop_url', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to product table'))
    op.drop_constraint(None, 'price_product_shop_url', type_='foreignkey')
    op.create_foreign_key('price_product_shop_url_product_id_fkey', 'price_product_shop_url', 'price_product', ['product_id'], ['id'])
    op.drop_constraint('uniq_product_id_shop_id_url', 'price_product_shop_url', type_='unique')
    op.create_unique_constraint('uniq_product_id_shop_id_url', 'price_product_shop_url', ['product_id', 'shop_id', 'url'])
    op.drop_column('price_product_shop_url', 'product_version_id')
    op.add_column('price_product_price', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to product table'))
    op.drop_constraint(None, 'price_product_price', type_='foreignkey')
    op.create_foreign_key('price_product_price_product_id_fkey', 'price_product_price', 'price_product', ['product_id'], ['id'])
    op.drop_constraint('uniq_product_id_shop_id_date_price', 'price_product_price', type_='unique')
    op.create_unique_constraint('uniq_product_id_shop_id_date_price', 'price_product_price', ['product_id', 'shop_id', 'date_price'])
    op.drop_column('price_product_price', 'product_version_id')
    op.add_column('price_product_image', sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to product table'))
    op.drop_constraint(None, 'price_product_image', type_='foreignkey')
    op.create_foreign_key('price_product_image_product_id_fkey', 'price_product_image', 'price_product', ['product_id'], ['id'])
    op.drop_column('price_product_image', 'product_version_id')
    # ### end Alembic commands ###
