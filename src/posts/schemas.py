from datetime import datetime

from sqlmodel import SQLModel

from src.posts.types import PostBodyType
from src.users.schemas import UserRead


class PostCreate(SQLModel):
    body: PostBodyType


class PostRead(SQLModel):
    id: int
    body: PostBodyType
    user: UserRead
    created_at: datetime


class PostUpdate(SQLModel):
    body: PostBodyType
