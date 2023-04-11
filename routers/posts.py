import sys
sys.path.append('..')
from sqlalchemy import func, desc
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from Blog.database import engine, SessionLocal
from .users import get_current_user, not_found_exception, get_user_exception

router = APIRouter(
    prefix="/posts",
    tags={"posts"},
    responses={401: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class CreatePost(BaseModel):
    content: str


@router.get("/all-posts/")
async def get_all_posts(db: Session = Depends(get_db)):
    # if user is None:
    #     raise get_user_exception()
    posts = db.query(models.Posts).all()
    return sorted(posts, key=lambda post: (post.last_update, post.id), reverse=True)


@router.get("/")
async def get_all_user_home_posts(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = db.query(models.Users) \
        .filter(models.Users.id == user.get("user_id")) \
        .first()
    following = current_user.follower
    posts = []
    my_post = db.query(models.Posts)\
        .filter(models.Posts.author_id == user.get("user_id"))\
        .all()
    posts.extend(my_post)
    for user in following:
        user_posts = db.query(models.Posts)\
            .filter(models.Posts.author_id == user.followed_id)\
            .all()
        posts.extend(user_posts)
    return sorted(posts, key=lambda post: (post.last_update, post.id), reverse=True)


@router.get("/my/")
async def get_my_posts(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = db.query(models.Users)\
        .filter(models.Users.id == user.get("user_id"))\
        .first()
    # posts = db.query(models.Posts).all()
    posts = current_user.posts
    return sorted(posts, key=lambda post: (post.last_update, post.id), reverse=True)


@router.get("/{post_id}")
async def get_post(post_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    posts = db.query(models.Posts)\
        .filter(post_id == models.Posts.id).first()
    if posts is None:
        raise not_found_exception()
    return posts


@router.get("/recent/")
async def get_recent_posts(db: Session = Depends(get_db)):
    recent_posts = db.query(models.Posts).order_by(desc(models.Posts.last_update)).limit(3).all()
    return recent_posts


@router.post("/")
async def create_new_post(post: CreatePost, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    post_model = models.Posts()
    post_model.author_id = user.get("user_id")
    post_model.content = post.content
    db.add(post_model)
    db.commit()
    return post_model


@router.put("/{post_id}")
async def edit_post(post_id: int, post: CreatePost, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_post = db.query(models.Posts)\
        .filter(models.Posts.author_id == user.get("user_id"))\
        .filter(post_id == models.Posts.id).first()
    if current_post is None:
        raise not_found_exception()
    current_post.content = post.content
    current_post.last_update = func.now()
    db.add(current_post)
    db.commit()
    return current_post


@router.delete("/{post_id}")
async def delete_post(post_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_post = db.query(models.Posts)\
        .filter(models.Posts.author_id == user.get("user_id"))\
        .filter(post_id == models.Posts.id).first()
    if current_post is None:
        raise not_found_exception()
    db.delete(current_post)
    db.commit()
    return current_post


@router.get("/fix/")
async def fix(db: Session = Depends(get_db)):
    for i in range(1, 1000):
        current = db.query(models.Posts).filter(models.Posts.id == i).first()
        if current is None:
            continue
        current.importance = db.query(func.sum(models.Votes.vote)).filter(models.Votes.post_id == i).scalar() or 0
        db.add(current)
        db.commit()
    raise HTTPException(status_code=200, detail="fixed")

