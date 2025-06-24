from datetime import datetime

from sqlmodel import Field, SQLModel


class PostCreate(SQLModel):
    title: str = Field(min_length=2, max_length=64)
    body: str = Field(min_length=10)


class PostRead(SQLModel):
    id: int
    title: str
    body: str
    user_id: int
    created_at: datetime
    updated_at: datetime


class PostUpdate(SQLModel):
    title: str = Field(min_length=2, max_length=64)
    body: str = Field(min_length=10)
