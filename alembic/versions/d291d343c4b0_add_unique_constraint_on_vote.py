"""add unique constraint on vote

Revision ID: d291d343c4b0
Revises: 
Create Date: 2023-02-26 18:49:10.390292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd291d343c4b0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        'uq1',
        'votes',
        ['user_id', 'post_id']
    )


def downgrade():
    op.drop_constraint('uq1', 'votes')
