import random

from sqlalchemy.orm import Session
from datetime import datetime
# from Blog import models
from models import Users, Posts, Comments, Votes, Followers, Friendships
from database import engine, Base
from random import choice

Base.metadata.create_all(bind=engine)

db = Session(bind=engine)

# Add 10 to 15 users
# users_count = choice(range(10, 16))
# for i in range(users_count):
#     user = Users(
#         email=f'user{i}@example.com',
#         username=f'user{i}',
#         first_name=f'User{i}',
#         last_name=f'Lastname{i}',
#         hashed_password=f'password{i}'
#     )
#     db.add(user)
#     db.commit()

# Add 10 to 15 posts
# posts_count = choice(range(1, 2))
# users = db.query(Users).filter(Users.id == 9).all()
# for i in range(posts_count):
#     post = Posts(
#         content=f'This is post {i}',
#         author=choice(users)
#     )
#     db.add(post)
#     db.commit()

# Add 10 to 15 comments
# comments_count = choice(range(10, 16))
# users = db.query(Users).all()
# posts = db.query(Posts).all()
# for i in range(comments_count):
#     comment = Comments(
#         content=f'This is comment {i}',
#         author=choice(users),
#         post=choice(posts)
#     )
#     db.add(comment)
#     db.commit()

# Add 10 to 15 votes
# votes_count = choice(range(30, 40))
# users = db.query(Users).all()
# posts = db.query(Posts).all()
# for i in range(votes_count):
#     vote = Votes(
#         vote=choice([-1, 1]),
#         user=choice(users),
#         post=choice(posts)
#     )
#     db.add(vote)
#     db.commit()

# Add 10 to 15 followers
# followers_count = choice(range(15, 20))
# users = db.query(Users).all()
# for i in range(followers_count):
#     follower = None
#     follower_id = choice(users).id
#     followed_id = choice([user.id for user in users if user.id != follower_id])
#     follower = Followers(
#         follower_id=follower_id,
#         followed_id=followed_id
#     )
#
#     db.add(follower)
#     db.commit()


# Add 10 to 15 friends
friends_count = choice(range(15, 20))
users = db.query(Users).all()
for i in range(friends_count):
    friend = None
    sender_id = choice(users).id
    receiver_id = choice(users).id
    cur_state = random.randint(0, 2)
    friend = Friendships(
        # id=1,
        request_sender_id=sender_id,
        request_receiver_id=receiver_id,
        state=cur_state
    )
    # print(friend.request_sender_id)
    # print(friend.id)
    db.add(friend)
    db.commit()
