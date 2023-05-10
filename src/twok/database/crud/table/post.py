import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Post as PostModel


class Post(Table):
    table = PostModel

    def __init__(self, session: sqlalchemy.orm.session.Session):
        super().__init__(session)

        self.main_column = PostModel.title
