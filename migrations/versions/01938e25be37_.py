"""empty message

Revision ID: 01938e25be37
Revises: fd82f8fb41f1
Create Date: 2021-10-10 20:07:25.909875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01938e25be37'
down_revision = 'fd82f8fb41f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('imp_catalog_page_url_idx', 'imp_catalog_page', ['url'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('imp_catalog_page_url_idx', table_name='imp_catalog_page')
    # ### end Alembic commands ###