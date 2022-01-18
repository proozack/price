"""empty message

Revision ID: fcb0be4b812f
Revises: dc0380d73295
Create Date: 2021-12-05 22:56:27.514764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcb0be4b812f'
down_revision = 'dc0380d73295'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tager_brand_assignment', sa.Column('tager_brand_id', sa.Integer(), nullable=True, comment='FK to tager_brand.id table'))
    op.create_foreign_key(None, 'tager_brand_assignment', 'tager_brand', ['tager_brand_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tager_brand_assignment', type_='foreignkey')
    op.drop_column('tager_brand_assignment', 'tager_brand_id')
    # ### end Alembic commands ###