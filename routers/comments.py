import sys
sys.path.append('..')

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
import models
from Blog.database import engine, SessionLocal
from routers.users import get_current_user, not_found_exception, get_user_exception


router = APIRouter(
    prefix="/comments",
    tags={"comments"},
    responses={401: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class CreateComment(BaseModel):
    content: str
    post_id: int


class EditComment(BaseModel):
    content: str


@router.get("/")
async def get_all_comments(db: Session = Depends(get_db)):
    comments = db.query(models.Comments).all()
    return comments


@router.get("/by_post/{post_id}")
async def get_comments_from_post(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(models.Comments)\
        .filter(post_id == models.Comments.post_id).all()
    if comments is None:
        raise not_found_exception()
    return comments


@router.get("/{comment_id}")
async def get_comments_by_id(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(models.Comments)\
        .filter(comment_id == models.Comments.id).first()
    if comment is None:
        raise not_found_exception()
    return comment


@router.post("/")
async def create_new_comment(comment: CreateComment, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    comment_model = models.Comments()
    comment_model.author_id = user.get("user_id")
    comment_model.content = comment.content
    comment_model.post_id = comment.post_id
    db.add(comment_model)
    db.commit()
    return comment_model


@router.post("/reply/{parent_id}")
async def create_new_reply(parent_id: int, comment: CreateComment, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    comment_model = models.Comments()
    comment_model.author_id = user.get("user_id")
    comment_model.content = comment.content
    comment_model.post_id = comment.post_id
    comment_model.parent_id = parent_id
    db.add(comment_model)
    db.commit()
    return comment_model


@router.put("/{comment_id}")
async def edit_comment(comment_id: int, comment: EditComment, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_comment = db.query(models.Comments)\
        .filter(models.Comments.author_id == user.get("user_id"))\
        .filter(comment_id == models.Comments.id).first()
    if current_comment is None:
        raise not_found_exception()
    current_comment.content = comment.content
    current_comment.last_update = func.now()
    db.add(current_comment)
    db.commit()
    return current_comment


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_comment = db.query(models.Comments)\
        .filter(models.Comments.author_id == user.get("user_id"))\
        .filter(comment_id == models.Comments.id).first()
    if current_comment is None:
        raise not_found_exception()
    db.delete(current_comment)
    db.commit()
    return current_comment


