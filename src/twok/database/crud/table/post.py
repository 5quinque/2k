from typing import Optional

import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Post as PostModel
from twok.database.models import Board as BoardModel


class Post(Table):
    table = PostModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = PostModel.title

    def create(self, filter=None, **kwargs: dict):
        db_post = super().create(filter, **kwargs)

        if db_post:
            self.update(self.root_parent(db_post), latest_reply_date=db_post.date)

        return db_post

    def root_parent(self, post: PostModel):
        if post.parent:
            return self.root_parent(post.parent)

        return post

    def search(
        self,
        query,
        board_name: Optional[str]=None,
        skip=0,
        limit=20
    ):
        """Search for an entity by name

        Args:
            query (str): String to search for
            board_name (str, optional): Name of board to search in. Defaults to None.
            skip (int, optional): Number of entities to skip pass. Defaults to 0.
            limit (int, optional): Number of entities to return. Defaults to 20.
        Returns:
            list[entity]: List of entities

        n.b.
            This is a very simple search that just looks for the query string anywhere in the title.
            It's not very good, but it's good enough for now.
        """
        if board_name:
            db_board = self.get(board_name, table=BoardModel)
            if not db_board:
                return False

            board_id = db_board.board_id

            return (
                self._session.query(self.table)
                .filter(self.table.title.ilike(f"%{query}%"))
                .filter(self.table.board_id == board_id)
                # .order_by(order_by)
                .offset(skip)
                .limit(limit)
                .all()
            )

        return (
            self._session.query(self.table)
            .filter(self.table.title.ilike(f"%{query}%"))
            # .order_by(order_by)
            .offset(skip)
            .limit(limit)
            .all()
        )