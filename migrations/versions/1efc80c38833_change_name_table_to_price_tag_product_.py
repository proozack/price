"""change name table to price_tag_product and add new table price_tag_ofert

Revision ID: 1efc80c38833
Revises: 1e2dc8bfb3c8
Create Date: 2020-11-02 21:02:34.101535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1efc80c38833'
down_revision = '1e2dc8bfb3c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_tag_ofert', sa.Column('tag_product_id', sa.Integer(), nullable=False, comment='FK to tag table'))
    op.drop_constraint('price_tag_ofert_tag_id_fkey', 'price_tag_ofert', type_='foreignkey')
    op.create_foreign_key(None, 'price_tag_ofert', 'price_tag_ofert', ['tag_product_id'], ['id'])
    op.drop_column('price_tag_ofert', 'tag_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('price_tag_ofert', sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to tag table'))
    op.drop_constraint(None, 'price_tag_ofert', type_='foreignkey')
    op.create_foreign_key('price_tag_ofert_tag_id_fkey', 'price_tag_ofert', 'price_tag', ['tag_id'], ['id'])
    op.drop_column('price_tag_ofert', 'tag_product_id')
    # ### end Alembic commands ###
