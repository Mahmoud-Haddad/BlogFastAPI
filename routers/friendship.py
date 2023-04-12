import sys
from sqlalchemy.sql.expression import or_
from starlette import status

sys.path.append('..')
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from routers.users import get_current_user, not_found_exception, get_user_exception

router = APIRouter(
    prefix="/friendship",
    tags={"friendship"},
    responses={401: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.post("/")
async def send_request(receiver_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    sender_id = user.get("user_id")
    request_model = models.Friendships()
    request_model.request_sender_id = sender_id
    request_model.request_receiver_id = receiver_id
    request_model.state = 0
    db.add(request_model)
    db.commit()
    return request_model


@router.get("/my-requests/")
async def my_friend_requests(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    receiver_id = user.get("user_id")
    requests = db.query(models.Friendships)\
                .filter(models.Friendships.request_receiver_id == receiver_id)\
                .filter(models.Friendships.state == 0)\
                .all()
    if len(requests) == 0:
        raise HTTPException(status_code=200, detail="no requests")
    return requests


@router.get("/my-friends/")
async def my_friends(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    requests = db.query(models.Friendships)\
                .filter(or_(models.Friendships.request_receiver_id == current_user,
                            models.Friendships.request_sender_id == current_user))\
                .filter(models.Friendships.state == 1)\
                .all()
    if len(requests) == 0:
        raise HTTPException(status_code=200, detail="no friends")
    return requests


@router.get("/my-blocklist/")
async def my_blocklist(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    requests = db.query(models.Friendships)\
                .filter(models.Friendships.request_sender_id == current_user)\
                .filter(models.Friendships.state == 2)\
                .all()
    if len(requests) == 0:
        raise HTTPException(status_code=200, detail="no user blocked")
    return requests


@router.delete("/cancel/")
async def cancel_request(receiver_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    request = db.query(models.Friendships)\
        .filter(models.Friendships.request_receiver_id == receiver_id)\
        .filter(models.Friendships.request_sender_id == current_user).first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if request.state != 0:
        raise not_found_exception
    db.delete(request)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")


@router.delete("/delete-request/")
async def delete_request(sender_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    request = db.query(models.Friendships)\
        .filter(models.Friendships.request_receiver_id == current_user)\
        .filter(models.Friendships.request_sender_id == sender_id).first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if request.state != 0:
        raise not_found_exception
    db.delete(request)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")


@router.delete("/unfriend/")
async def unfriend(receiver_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    request = db.query(models.Friendships)\
        .filter(models.Friendships.request_receiver_id == current_user)\
        .filter(models.Friendships.request_sender_id == receiver_id).first()
    if len(request) == 0:
        request = db.query(models.Friendships) \
            .filter(models.Friendships.request_receiver_id == receiver_id) \
            .filter(models.Friendships.request_sender_id == current_user).first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if request.state != 1:
        raise not_found_exception
    db.delete(request)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")


@router.put("/accept/")
async def accept_request(sender_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    request = db.query(models.Friendships) \
        .filter(models.Friendships.request_receiver_id == current_user) \
        .filter(models.Friendships.request_sender_id == sender_id).first()
    if (request is None) or (request.state != 0):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    request.state = 1
    db.add(request)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")


@router.post("/block/")
async def block_user(receiver_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    request = db.query(models.Friendships) \
        .filter(models.Friendships.request_receiver_id == receiver_id) \
        .filter(models.Friendships.request_sender_id == current_user).first()
    if len(request) == 0:
        request = db.query(models.Friendships) \
            .filter(models.Friendships.request_receiver_id == current_user) \
            .filter(models.Friendships.request_sender_id == receiver_id).first()
    if request is not None:
        db.delete(request)
        db.commit()
    block_model = models.Friendships()
    block_model.request_sender_id = current_user
    block_model.request_receiver_id = receiver_id
    block_model.state = 2
    db.add(block_model)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")


@router.delete("/unblock/")
async def unblock_user(receiver_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    current_user = user.get("user_id")
    blocked = db.query(models.Friendships)\
        .filter(models.Friendships.request_receiver_id == receiver_id)\
        .filter(models.Friendships.request_sender_id == current_user).first()
    if blocked is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')
    if blocked.state != 2:
        raise not_found_exception
    db.delete(blocked)
    db.commit()
    raise HTTPException(status_code=200, detail="successful")





