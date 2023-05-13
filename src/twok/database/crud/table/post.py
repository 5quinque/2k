import sqlalchemy

from twok.database.crud.table import Table
from twok.database.models import Post as PostModel


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