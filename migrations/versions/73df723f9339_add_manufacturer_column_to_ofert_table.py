"""add manufacturer column to ofert table

Revision ID: 73df723f9339
Revises: 
Create Date: 2020-09-26 23:45:55.835677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73df723f9339'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_ofert', sa.Column('manufacturer', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('price_ofert', 'manufacturer')
    # ### end Alembic commands ###
