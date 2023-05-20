"""pydantic models used in fastapi
"""

from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile
from pydantic import BaseModel
from pydantic.networks import EmailStr


class UserBase(BaseModel):
    name: str
    email_address: EmailStr


class UserCreate(UserBase):
    plaintext_password: str


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class BoardBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class BoardCreate(BoardBase):
    pass


class PostBase(BaseModel):
    title: str
    message: str = None


class PostCreate(PostBase):
    board_name: str
    parent_id: int = None
    file_id: Optional[int] = None


class Post(PostBase):
    post_id: int
    board: BoardBase
    date: str = None
    file: Optional["FileBase"] = None
    parent_id: int = None
    children: list["Post"] = []
    latest_reply_date: str = None

    class Config:
        orm_mode = True


class FileBase(BaseModel):
    file_id: int
    file_name: str
    file_hash: str
    content_type: str
    post_id: int = None

    class Config:
        orm_mode = True


class Board(BoardBase):
    board_id: int
    posts: list[Post]

    class Config:
        orm_mode = True


class SearchListResponse(BaseModel):
    posts: list[Optional[Post]]
    boards: list[Optional[Board]]


class Requester(BaseModel):
    ip_address: str
    last_post_time: Optional[datetime] = None


class HealthCheckResponse(BaseModel):
    status: str
    time: datetime


Post.update_forward_refs()
