from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile

from twok import files
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
        parent_id=post.parent_id,
    )

    return db_post

@post_router.post("/upload", response_model=schemas.FileBase, status_code=201)
async def upload_file(db: dependencies.database, file: UploadFile, post_id: Optional[int] = None):
    file_hash = await files.save_upload_file(file)

    # check if post exists and return 404 if not
    if post_id:
        db_post = db.post.get(filter=[models.Post.post_id == post_id])
        if not db_post:
            raise HTTPException(status_code=404, detail="Post not found")

    db_file = db.file.create(
        filter=None,
        file_name=file.filename,
        file_hash=file_hash,
        content_type=file.content_type,
        post_id=post_id,
    )

    if not db_file:
        raise HTTPException(status_code=409, detail="File already exists")

    return db_file
