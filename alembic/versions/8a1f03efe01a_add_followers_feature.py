"""add followers feature

Revision ID: 8a1f03efe01a
Revises: f0a93d6e36bf
Create Date: 2023-03-04 16:07:36.468385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a1f03efe01a'
down_revision = 'f0a93d6e36bf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "followers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("follower_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("followed_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
    )
    sa.CheckConstraint('follower_id != followed_id', name='no_self_follow'),
    op.create_unique_constraint(
        'uq_followers_follower_id_followed_id',
        'followers',
        ['follower_id', 'followed_id']
    )


def downgrade():
    op.drop_table("followers")
