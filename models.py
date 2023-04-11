from sqlalchemy import Boolean, String, Integer, Column, ForeignKey, DateTime, func, Text, UniqueConstraint, \
    CheckConstraint, event
from sqlalchemy.orm import relationship, validates
from database import Base
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class Followers(Base):
    __tablename__ = "followers"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    followed_id = Column(Integer, ForeignKey("users.id"))

    user_followed = relationship("Users", back_populates="followed", foreign_keys=[followed_id])
    user_follower = relationship("Users", back_populates="follower", foreign_keys=[follower_id])

    # Check constraint to prevent users from following themselves
    __table_args__ = (
        CheckConstraint('follower_id != followed_id', name='check_follower_followed'),
    )


class Friendships(Base):
    __tablename__ = "friendships"
    id = Column(Integer, primary_key=True, index=True)
    request_sender_id = Column(Integer, ForeignKey('users.id'))
    request_receiver_id = Column(Integer, ForeignKey('users.id'))
    state = Column(Integer, nullable=False, default=0)
    # (0 pending) (1 accepted) (2 blocked)
    user_request_sender = relationship("Users", back_populates="request_sender", foreign_keys=[request_sender_id])
    user_request_receiver = relationship("Users", back_populates="request_receiver", foreign_keys=[request_receiver_id])


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    posts = relationship("Posts", back_populates="author")
    comments = relationship("Comments", back_populates="author")
    vote = relationship("Votes", back_populates="user")
    follower = relationship("Followers", back_populates="user_follower", foreign_keys=[Followers.follower_id])
    followed = relationship("Followers", back_populates="user_followed", foreign_keys=[Followers.followed_id])
    request_sender = relationship("Friendships", back_populates="user_request_sender",
                                  foreign_keys=[Friendships.request_sender_id])
    request_receiver = relationship("Friendships", back_populates="user_request_receiver",
                                    foreign_keys=[Friendships.request_receiver_id])


class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, default=func.now())
    deleted_at = Column(DateTime,  nullable=True)
    importance = Column(Integer, default=0)
    author = relationship("Users", back_populates="posts")
    comment = relationship("Comments", back_populates="post")
    vote = relationship("Votes", back_populates="post")


class Comments(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(Text)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    last_update = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime,  nullable=True)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)

    author = relationship("Users", back_populates="comments")
    post = relationship("Posts", back_populates="comment")
    reply = relationship("Comments")


class Votes(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    vote = Column(Integer)

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='uq_my_table_post_id_user_id'),)

    post = relationship("Posts", back_populates="vote")
    user = relationship("Users", back_populates="vote")

# triggers functions


def check_friendship_request(mapper, connection, target):
    if target.request_sender_id == target.request_receiver_id:
        raise ValueError("request_sender_id cannot be equal to request_receiver_id")


def check_duplicate_friendship_request(mapper, connection, target):
    result = connection.execute(
        Friendships.__table__.select().where(
            Friendships.request_sender_id == target.request_sender_id
        ).where(
            Friendships.request_receiver_id == target.request_receiver_id
        )
    ).fetchall()
    if len(result) > 0:
        raise IntegrityError("Duplicate friendship request")
    result = connection.execute(
        Friendships.__table__.select().where(
            Friendships.request_sender_id == target.request_receiver_id
        ).where(
            Friendships.request_receiver_id == target.request_sender_id
        )
    ).fetchall()
    if len(result) > 0:
        raise IntegrityError("Duplicate friendship request")


# triggers
event.listen(Friendships, 'before_insert', check_friendship_request)
event.listen(Friendships, 'before_insert', check_duplicate_friendship_request)


