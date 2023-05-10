from datetime import datetime
from fastapi import APIRouter

from twok.api import dependencies
from twok.database import schemas, models

post_router = APIRouter(
    prefix="/post",
    tags=["Post"],
    responses={404: {"description": "Not found"}},
)


@post_router.get("", response_model=list[schemas.Post])
def read_posts(
    pagination: dependencies.pagination_parameters, db: dependencies.database
):
    db_posts = db.api_get(models.Post)

    return db_posts


@post_router.get("/{post_id}", response_model=schemas.Post)
def read_post(post: dependencies.post):
    return post


@post_router.post("", response_model=schemas.Post, status_code=201)
def create_post(
    post: schemas.PostCreate, db: dependencies.database
):
    db_post = db.post.create(
        filter=None,
        title=post.title,
        message=post.message,
        date=datetime.now(),
        board_id=1,
    )

    return db_post