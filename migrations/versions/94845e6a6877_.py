"""empty message

Revision ID: 94845e6a6877
Revises: aeaba3dcbae5
Create Date: 2021-11-14 12:06:56.644661

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '94845e6a6877'
down_revision = 'aeaba3dcbae5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Tager_brand_assignment')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Tager_brand_assignment',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=False, comment='Is record is active'),
    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=False, comment='Is record is deleted'),
    sa.Column('created_by', sa.INTEGER(), autoincrement=False, nullable=False, comment='Who created record'),
    sa.Column('creation_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False, comment='Timestamp created record'),
    sa.Column('last_update_by', sa.INTEGER(), autoincrement=False, nullable=True, comment='Who last update record'),
    sa.Column('last_update_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='Timestamp last update record'),
    sa.Column('brand', sa.TEXT(), autoincrement=False, nullable=True, comment='Brand Name'),
    sa.Column('imp_catalog_page_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='FK to imp_catalog_page.id table'),
    sa.ForeignKeyConstraint(['imp_catalog_page_id'], ['imp_catalog_page.id'], name='Tager_brand_assignment_imp_catalog_page_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Tager_brand_assignment_pkey'),
    sa.UniqueConstraint('imp_catalog_page_id', name='Tager_brand_assignment_imp_catalog_page_id_key')
    )
    # ### end Alembic commands ###