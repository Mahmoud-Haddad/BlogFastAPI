import sys
sys.path.append('..')

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
import models
from Blog.database import engine, SessionLocal
from routers.users import get_current_user, not_found_exception, get_user_exception, already_voted


router = APIRouter(
    prefix="/votes",
    tags={"votes"},
    responses={401: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
async def get_all_votes(db: Session = Depends(get_db)):
    votes = db.query(models.Votes).all()
    return votes


@router.get("/by_post/{post_id}")
async def get_votes_from_post(post_id: int, db: Session = Depends(get_db)):
    votes = db.query(models.Votes.vote, models.Users.first_name)\
        .join(models.Users, and_(models.Users.id == models.Votes.user_id))\
        .filter(models.Votes.post_id == post_id)\
        .all()
    if votes is None:
        raise not_found_exception()
    return {"votes on post": votes}

#
# @router.get("/{comment_id}")
# async def get_comments_by_id(comment_id: int, db: Session = Depends(get_db)):
#     comment = db.query(models.Comments)\
#         .filter(comment_id == models.Comments.id).first()
#     if comment is None:
#         raise not_found_exception()
#     return comment


@router.post("/upvote/{post_id}")
async def create_new_upvote(post_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    check_vote = db.query(models.Votes)\
        .filter(models.Votes.user_id == user.get("user_id"))\
        .filter(models.Votes.post_id == post_id).first()
    current_post = db.query(models.Posts)\
        .filter(post_id == models.Posts.id).first()
    if current_post is None:
        raise not_found_exception()
    # return check_vote
    if check_vote is not None:
        if check_vote.vote == 1:
            raise already_voted()
            # raise HTTPException(status_code="413", detail="you can't vote more than once")
        else:
            current_post.importance += 2
            db.add(current_post)
            check_vote.vote = 1
            db.add(check_vote)
            db.commit()
            return check_vote

    current_post.importance += 1
    db.add(current_post)
    db.commit()
    vote_model = models.Votes()
    vote_model.user_id = user.get("user_id")
    vote_model.post_id = post_id
    vote_model.vote = 1
    db.add(vote_model)
    db.commit()
    return vote_model


@router.post("/downvote/{post_id}")
async def create_new_downvote(post_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    check_vote = db.query(models.Votes)\
        .filter(models.Votes.user_id == user.get("user_id"))\
        .filter(models.Votes.post_id == post_id).first()
    current_post = db.query(models.Posts) \
        .filter(post_id == models.Posts.id).first()
    if current_post is None:
        raise not_found_exception()
    if check_vote is not None:
        if check_vote.vote == -1:
            raise already_voted()
            # raise HTTPException(status_code="413", detail="you can't vote more than once")
        else:
            current_post.importance -= 2
            db.add(current_post)
            check_vote.vote = -1
            db.add(check_vote)
            db.commit()
            return check_vote

    current_post.importance -= 1
    db.add(current_post)
    db.commit()
    vote_model = models.Votes()
    vote_model.user_id = user.get("user_id")
    vote_model.post_id = post_id
    vote_model.vote = -1
    db.add(vote_model)
    db.commit()
    return vote_model


# @router.put("/{comment_id}")
# async def edit_comment(comment_id: int, comment: EditComment, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     current_comment = db.query(models.Comments)\
#         .filter(models.Comments.author_id == user.get("user_id"))\
#         .filter(comment_id == models.Comments.id).first()
#     if current_comment is None:
#         raise not_found_exception()
#     current_comment.content = comment.content
#     current_comment.last_update = func.now()
#     db.add(current_comment)
#     db.commit()
#     return current_comment
#
#
# @router.delete("/{comment_id}")
# async def delete_comment(comment_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is None:
#         raise get_user_exception()
#     current_comment = db.query(models.Comments)\
#         .filter(models.Comments.author_id == user.get("user_id"))\
#         .filter(comment_id == models.Comments.id).first()
#     if current_comment is None:
#         raise not_found_exception()
#     db.delete(current_comment)
#     db.commit()
#     return current_comment


