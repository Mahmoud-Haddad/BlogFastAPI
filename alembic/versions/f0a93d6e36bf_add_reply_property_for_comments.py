"""add reply property for comments

Revision ID: f0a93d6e36bf
Revises: 3eb1cd1997d4
Create Date: 2023-03-01 19:44:52.889326

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0a93d6e36bf'
down_revision = '3eb1cd1997d4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('comments', sa.Column('parent_id', sa.Integer, nullable=True, default=None))
    op.create_foreign_key('parent_fk', source_table="comments", referent_table="comments",
                          local_cols=['parent_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('parent_fk')
    op.drop_column('parent_id')
