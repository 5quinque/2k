import logging
import sqlalchemy
from typing import Optional

logger = logging.getLogger(__name__)


class Table:
    table: sqlalchemy.Table
    main_column: sqlalchemy.Column

    def __init__(self, session: sqlalchemy.orm.session.Session):
        self._session = session

    def get(
        self,
        name: Optional[str] = None,
        table: Optional[sqlalchemy.Table] = None,
        filter: Optional[list] = False,
    ):
        """Get an entity if one doesn't exist with the given name (or by given filter)
        Args:
            filter (bool, optional): Optional `where` list . Defaults to False which is filter by `this.main_column`.

        Returns:
            (object, None): pre-existing entity object, or `None` if no entity is found
        """
        if not table:
            table = self.table

        if not filter:
            filter = [self.main_column == name]

        entity = self._session.query(table).filter(*filter).first()

        if entity:
            return entity

    def create(self, filter=None, **kwargs: dict):
        """Create an entity
        Args:
            **kwargs: Entity attributes

        Returns:
            (object, None): newly created entity object.
        """
        if not filter:
            filter = [self.main_column == kwargs[self.main_column.name]]

        if self.get(filter=filter):
            return False

        entity = self.table(**kwargs)
        self._session.add(entity)
        self._session.commit()

        return entity

    def update(self, entity, **kwargs: dict) -> object:
        """Update an entity

        Args:
            entity (entity): Entity to update
        """

        for key, value in kwargs.items():
            setattr(entity, key, value)

        self._session.commit()

        return entity

    def delete(self, entity):
        """Delete an entity

        Args:
            entity (entity): Entity to delete
        """
        self._session.delete(entity)
        self._session.commit()

    def search(self, query, query_column: Optional[sqlalchemy.Column] = None):
        """Search for an entity by name

        Args:
            query (str): String to search for
            query_column (sqlalchemy.Column, optional): Column to search in. Defaults to None which is `this.main_column`.

        Returns:
            list[entity]: List of entities

        n.b.
            This is a very simple search that just looks for the query string anywhere in the title.
            It's not very good, but it's good enough for now.
        """
        if not query_column:
            query_column = self.main_column

        return (
            self._session.query(self.table)
            .filter(query_column.ilike(f"%{query}%"))
            .all()
        )
