import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Board as BoardModel


class Board(Table):
    table = BoardModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = BoardModel.name
