import sys
sys.path.append('..')
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from routers.users import get_current_user, not_found_exception, get_user_exception

router = APIRouter(
    prefix="/following",
    tags={"following"},
    responses={401: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/my_followers/")
async def get_my_followers(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = db.query(models.Users)\
        .filter(models.Users.id == user.get("user_id"))\
        .first()
    followers = current_user.followed
    return followers


@router.get("/my_followings/")
async def get_my_following(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = db.query(models.Users)\
        .filter(models.Users.id == user.get("user_id"))\
        .first()
    followers = current_user.follower
    return followers


@router.get("/followers/{user_id}")
async def get_user_followers(user_id, db: Session = Depends(get_db)):
    current_user = db.query(models.Users)\
        .filter(models.Users.id == user_id)\
        .first()
    followers = current_user.followed
    return followers


@router.get("/followings/{user_id}")
async def get_user_followings(user_id, db: Session = Depends(get_db)):
    current_user = db.query(models.Users)\
        .filter(models.Users.id == user_id)\
        .first()
    followings = current_user.follower
    return followings


@router.post("/{followed_id}")
async def create_new_following(followed_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    follower_id = user.get("user_id")
    followed_user = db.query(models.Users).filter(models.Users.id == followed_id).first()
    if followed_user is None:
        raise not_found_exception
    following_check = db.query(models.Followers)\
        .filter(models.Followers.follower_id == follower_id)\
        .filter(models.Followers.followed_id == followed_id)\
        .first()
    if following_check is not None:
        raise HTTPException(status_code=404, detail="already followed")
    new_following = models.Followers()
    new_following.follower_id = follower_id
    new_following.followed_id = followed_id
    db.add(new_following)
    db.commit()
    return new_following


@router.delete("/{followed_id}")
async def unfollowing_user(followed_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    follower_id = user.get("user_id")
    followed_user = db.query(models.Users).filter(models.Users.id == followed_id).first()
    if followed_user is None:
        raise not_found_exception
    following_check = db.query(models.Followers)\
        .filter(models.Followers.follower_id == follower_id)\
        .filter(models.Followers.followed_id == followed_id)\
        .first()
    if following_check is None:
        raise HTTPException(status_code=404, detail="user is not followed")
    db.delete(following_check)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")

