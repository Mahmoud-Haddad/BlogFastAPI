from fastapi import FastAPI
import models
from database import engine, SessionLocal
from routers import users, posts, comments
from Blog.routers import votes, following, friendship

# from routers import auth, todos

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(votes.router)
app.include_router(following.router)
app.include_router(friendship.router)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


