"""empty message

Revision ID: 5649c3b1f211
Revises: 5f119aed69e8
Create Date: 2021-11-21 23:21:57.376223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5649c3b1f211'
down_revision = '5f119aed69e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('imp_catalog_page_status', sa.Column('specific_category_date', sa.Date(), nullable=True, comment='Tagged date'))
    op.drop_column('imp_catalog_page_status', 'specific_category__date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('imp_catalog_page_status', sa.Column('specific_category__date', sa.DATE(), autoincrement=False, nullable=True, comment='Tagged date'))
    op.drop_column('imp_catalog_page_status', 'specific_category_date')
    # ### end Alembic commands ###
