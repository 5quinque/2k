import logging
from typing import Dict, Union

import sqlalchemy

from twok.database.models import (
    Board,
    Post,
    User,
)

from twok.database.crud.table.board import Board as BoardCRUD
from twok.database.crud.table.post import Post as PostCRUD
from twok.database.crud.table.user import User as UserCRUD

logger = logging.getLogger(__name__)


class DB:
    def __init__(self, session: sqlalchemy.orm.session.Session):
        self._session = session

        self.board = BoardCRUD(self._session)
        self.post = PostCRUD(self._session)
        self.user = UserCRUD(self._session)

    def search_all(self, query):
        """Search for an entity by name

        Args:
            query (str): String to search for

        Returns:
            dict[str, list[entity]]: List of entities

        n.b.
            This is a very simple search that just looks for the query string anywhere in the title.
            It's not very good, but it's good enough for now.
        """
        return {
            "post": self.post.search(query),
        }

    def api_get(self, table, filter=[], skip=0, limit=100):
        """Used within the API to get pagination list of entities

        Args:
            table (Table): Table object you want to query
            filter (list): List of filters to apply
            skip (int, optional): Number of entities to skip pass. Defaults to 0.
            limit (int, optional): Number of entities to return. Defaults to 100.

        Returns:
            list[entity]: List of entities
        """
        return (
            self._session.query(table).filter(*filter).offset(skip).limit(limit).all()
        )

    def add_board(self, board_name: str) -> Union[bool, Board]:
        """
        Adds a new board to the database if it doesn't already exist.

        Parameters:
            board_name (str): The name of the board to add to the database.

        Returns:
            Union[bool, Board]: False if the board already exists in the database,
            otherwise returns the entity representing the added board.
        """
        if self.get(
            Board,
            filter=[
                Board.name == board_name,
            ],
        ):
            return False
        return self.create(
            Board,
            filter=[
                Board.name == board_name,
            ],
            name=board_name,
        )

    def add_post(self, board_name: str, post: Dict):
        """
        Adds a new post to the database if it doesn't already exist.

        Parameters:
            board_name (str): The name of the board to add the post to.
            post (dict): The post to add to the database.

        Returns:
            Union[bool, Post]: False if the post already exists in the database,
            otherwise returns the entity representing the added post.
        """
        # if self.get(
        #     Post,
        #     filter=[
        #         Post.board.has(name=board_name),
        #         Post.post_id == post["post_id"],
        #     ],
        # ):
        #     return False
        return self.create(
            Post,
            filter=[
                Post.board.has(name=board_name),
                # Post.post_id == post["post_id"],
            ],
            **post,
        )
