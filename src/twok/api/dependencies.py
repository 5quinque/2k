from datetime import datetime
from typing import Annotated, Dict, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from twok.api.config import Settings
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


def _settings() -> Settings:
    return Settings()


def _pagination_parameters(page: int = 1, settings: Settings = Depends(_settings)):
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

    filter = [models.Post.board_id == board.board_id and models.Post.parent_id == None]

    db_posts = db.api_get(
        table=models.Post,
        filter=filter,
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


def _post_prechecks(
    request: Request,
    db: DB = Depends(_db),
    settings: Settings = Depends(_settings),
):
    # Get the IP address of the requester from the request object
    requester_ip_addr = request.client.host

    # Check if the requester IP address exists in the database
    db_requester = db.requester.get(
        filter=[models.Requester.ip_address == requester_ip_addr]
    )

    if db_requester:
        # Retrieve the last post time from the database
        last_post_time: str = db_requester.last_post_time
        current_time: datetime = datetime.now()

        # Calculate the time difference between the current time and the last post time
        # and represent it as a timedelta object
        time_difference = current_time - datetime.strptime(
            last_post_time, "%Y-%m-%d %H:%M:%S.%f"
        )

        # If the time difference is less than the limit, return False to indicate that the post is not allowed
        if time_difference < settings.post_time_limit:
            raise HTTPException(status_code=429, detail="Probably posting too fast")

        db.requester.update(db_requester, last_post_time=current_time)
    else:
        # If the requester IP address doesn't exist in the database, create a new entry
        # db_requester = models.Requester(ip_address=requester_ip_addr)
        db.requester.create(
            filter=None,
            ip_address=requester_ip_addr,
            last_post_time=datetime.now(),
        )

    # Return True to indicate that the post is allowed
    return True


auth = Annotated[Auth, Depends(_auth)]
current_user = Annotated[bool, Depends(_current_user)]
database = Annotated[DB, Depends(_db)]
pagination_parameters = Annotated[dict, Depends(_pagination_parameters)]
page_count = Annotated[int, Depends(_page_count)]
post = Annotated[schemas.Post, Depends(_post)]
posts = Annotated[list[schemas.Post], Depends(_posts)]
board = Annotated[schemas.Board, Depends(_board)]
search_posts = Annotated[list[schemas.Post], Depends(_search_posts)]
post_prechecks = Annotated[bool, Depends(_post_prechecks)]
