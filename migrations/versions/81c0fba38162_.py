"""empty message

Revision ID: 81c0fba38162
Revises: 01938e25be37
Create Date: 2021-10-13 10:30:35.287517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81c0fba38162'
down_revision = '01938e25be37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'imp_product_page', ['imp_catalog_page_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'imp_product_page', type_='unique')
    # ### end Alembic commands ###
