from fastapi import APIRouter

from twok.api import dependencies
from twok.database import schemas, models

board_router = APIRouter(
    prefix="/board",
    tags=["Board"],
    responses={404: {"description": "Not found"}},
)


@board_router.get("", response_model=list[schemas.Board])
def read_boards(
    pagination: dependencies.pagination_parameters, db: dependencies.database
):
    db_boards = db.api_get(models.Board)

    return db_boards


@board_router.get("/{board_name}", response_model=schemas.Board)
def read_board(board: dependencies.board):
    return board


@board_router.post("", response_model=schemas.Board, status_code=201)
def create_board(
    board: schemas.BoardCreate, db: dependencies.database
):
    db_board = db.board.create(
        filter=None,
        name=board.name,
    )

    return db_board