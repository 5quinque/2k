from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from twok.api.services.auth import Auth
from twok.database.crud import DB
from twok.database import schemas, models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _db(request: Request):
    db_session = request.app.state.db_pool.get_session()

    db = DB(session=db_session)
    try:
        yield db
    finally:
        db_session.close()
        del db


async def _pagination_parameters(page: int = 1):
    skip = (page - 1) * 50
    limit = 50

    return {"skip": skip, "limit": limit}


def _auth(db: DB = Depends(_db)):
    auth = Auth(db)
    try:
        yield auth
    finally:
        del auth


async def _current_user(
    auth: Auth = Depends(_auth), token: str = Depends(oauth2_scheme)
):
    user = auth.user(token)
    if user:
        return user

    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _post(post_id: int, db: DB = Depends(_db)):
    db_post = db.post.get(filter=[models.Post.post_id == post_id])

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return db_post


def _board(board_id: int, db: DB = Depends(_db)):
    db_board = db.board.get(filter=[models.Board.board_id == board_id])

    if db_board is None:
        raise HTTPException(status_code=404, detail="Board not found")

    return db_board


auth = Annotated[Auth, Depends(_auth)]
current_user = Annotated[bool, Depends(_current_user)]
database = Annotated[DB, Depends(_db)]
pagination_parameters = Annotated[dict, Depends(_pagination_parameters)]
post = Annotated[schemas.Post, Depends(_post)]
board = Annotated[schemas.Board, Depends(_board)]
