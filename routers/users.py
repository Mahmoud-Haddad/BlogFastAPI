import sys
sys.path.append('..')
from fastapi import Depends, HTTPException, status, APIRouter
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

secret_key = "WhatEverIWant"
algo = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix="/user",
    tags={"user"},
    responses={401: {"user": "Not authorized"}}
)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain, hashed):
    return bcrypt_context.verify(plain, hashed)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if verify_password(password, user.hashed_password):
        return user
    return False


def create_auth_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, secret_key, algo)


async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, secret_key, algo)
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise get_user_exception()


@router.get("/")
async def get_all_users(db: Session = Depends(get_db)):
    try:
        users = db.query(models.Users).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_new_user(new_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.username = new_user.username
    create_user_model.email = new_user.email
    create_user_model.first_name = new_user.first_name
    create_user_model.last_name = new_user.last_name
    create_user_model.hashed_password = get_password_hash(new_user.password)
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()
    raise successful_added()


@router.post("/token")
async def login_token(form: OAuth2PasswordRequestForm = Depends(),
                      db: Session = Depends(get_db)):
    user = authenticate_user(form.username, form.password, db)
    if not user:
        raise token_exception()
    expire_token = timedelta(minutes=120)
    token = create_auth_token(user.username, user.id, expire_token)
    return {"token": token}


def successful_added():
    return HTTPException(status_code=201, detail='a new user added')


def not_found_exception():
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response


def already_voted():
    already_voted_exception_response = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="already voted",
    )
    return already_voted_exception_response

