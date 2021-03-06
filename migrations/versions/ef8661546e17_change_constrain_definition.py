"""Change constrain definition

Revision ID: ef8661546e17
Revises: 1fcfa0ff75a3
Create Date: 2020-10-06 21:39:24.241107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef8661546e17'
down_revision = '1fcfa0ff75a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('price_product_price_shop_id_fkey', 'price_product_price', type_='foreignkey')
    op.create_foreign_key(None, 'price_product_price', 'price_shop', ['shop_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'price_product_price', type_='foreignkey')
    op.create_foreign_key('price_product_price_shop_id_fkey', 'price_product_price', 'price_repo_image', ['shop_id'], ['id'])
    # ### end Alembic commands ###
