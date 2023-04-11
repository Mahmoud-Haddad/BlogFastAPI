"""add friendship.py table

Revision ID: 6249ab2c82ee
Revises: 8a1f03efe01a
Create Date: 2023-04-10 18:38:20.639173

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import event
from models import Friendships
# revision identifiers, used by Alembic.
revision = '6249ab2c82ee'
down_revision = '8a1f03efe01a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "friendships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("request_sender_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("request_receiver_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("state", sa.Integer, nullable=False),
    )

    def check_friendship_request(mapper, connection, target):
        if target.request_sender_id == target.request_receiver_id:
            raise ValueError("request_sender_id cannot be equal to request_receiver_id")

    event.listen(Friendships, 'before_insert', check_friendship_request)


def downgrade():
    op.drop_table("friendships")
