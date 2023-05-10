"""sqlalchemy models
"""
from sqlalchemy.orm import relationship
from sqlalchemy import (
    ForeignKey,
    Table,
    Column,
    Integer,
    String,
)

from twok.database import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    name = Column(String(32))
    email_address = Column(String(128))
    password_hash = Column(String(128))


class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=True)
    message = Column(String(512), nullable=True)
    date = Column(String(32), nullable=True)

    board_id = Column(ForeignKey("board.board_id"))
    board = relationship("Board", back_populates="posts")

    parent_id = Column(Integer, ForeignKey("post.post_id"), index=True, nullable=True)
    parent = relationship("Post", backref="children", remote_side=[post_id])

class Board(Base):
    __tablename__ = "board"

    board_id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    posts = relationship("Post", back_populates="board")
