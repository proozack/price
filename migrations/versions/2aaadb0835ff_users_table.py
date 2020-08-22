"""users table

Revision ID: 2aaadb0835ff
Revises: 7010c33a150a
Create Date: 2019-11-19 00:04:53.552253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2aaadb0835ff'
down_revision = '7010c33a150a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ims_workers', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ims_workers', 'ims_users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ims_workers', type_='foreignkey')
    op.drop_column('ims_workers', 'user_id')
    # ### end Alembic commands ###
