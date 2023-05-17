from typing import Annotated, Dict, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from twok.api.config import settings
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


def _pagination_parameters(page: int = 1):
    # Can you use a dataclass here, does it make sense to?
    skip = (page - 1) * settings.items_per_page

    return {"skip": skip, "limit": settings.items_per_page}


def _page_count(board_name: str, db: DB = Depends(_db)):
    page_count = db.board.page_count(board_name)

    if page_count is False:
        # specifically check for `is False` because page_count can be 0
        raise HTTPException(status_code=404, detail="Board not found")

    return page_count


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


def _posts(
    board_name: str,
    pagination: Dict = Depends(_pagination_parameters),
    db: DB = Depends(_db),
):
    board = db.board.get(filter=[models.Board.name == board_name])
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")

    db_posts = db.api_get(
        table=models.Post,
        filter=[models.Post.board_id == board.board_id],
        order_by=models.Post.latest_reply_date.desc(),
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    if db_posts is None:
        raise HTTPException(status_code=404, detail="Posts not found")

    return db_posts


def _board(board_name: str, db: DB = Depends(_db)):
    db_board = db.board.get(filter=[models.Board.name == board_name])

    if db_board is None:
        raise HTTPException(status_code=404, detail="Board not found")

    return db_board


def _search_posts(
    query: str,
    board_name: Optional[str] = None,
    pagination: Dict = Depends(_pagination_parameters),
    db: DB = Depends(_db),
):
    if board_name:
        db_board = db.board.get(filter=[models.Board.name == board_name])

    db_results = db.post.search(
        query=query,
        board_name=board_name,
        skip=pagination["skip"],
        limit=pagination["limit"],
    )

    if db_results is None:
        raise HTTPException(status_code=404, detail="Posts not found")

    return db_results


auth = Annotated[Auth, Depends(_auth)]
current_user = Annotated[bool, Depends(_current_user)]
database = Annotated[DB, Depends(_db)]
pagination_parameters = Annotated[dict, Depends(_pagination_parameters)]
page_count = Annotated[int, Depends(_page_count)]
post = Annotated[schemas.Post, Depends(_post)]
posts = Annotated[list[schemas.Post], Depends(_posts)]
board = Annotated[schemas.Board, Depends(_board)]
search_posts = Annotated[list[schemas.Post], Depends(_search_posts)]
