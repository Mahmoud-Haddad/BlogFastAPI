"""add vote column to post

Revision ID: 3eb1cd1997d4
Revises: d291d343c4b0
Create Date: 2023-02-26 19:27:40.882722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb1cd1997d4'
down_revision = 'd291d343c4b0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('importance', sa.Integer, default=0))


def downgrade():
    op.drop_column('posts', 'importance')
