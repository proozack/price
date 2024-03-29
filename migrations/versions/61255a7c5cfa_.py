"""empty message

Revision ID: 61255a7c5cfa
Revises: fcb0be4b812f
Create Date: 2021-12-15 08:24:53.938411

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61255a7c5cfa'
down_revision = 'fcb0be4b812f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tager_tagging_result', 'category')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tager_tagging_result', sa.Column('category', sa.TEXT(), autoincrement=False, nullable=False, comment='polish color name'))
    # ### end Alembic commands ###
