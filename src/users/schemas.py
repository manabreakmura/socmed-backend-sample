from datetime import datetime

from pydantic import EmailStr

from config.db import BaseSchema
from posts.schemas import PostResponseSchema


class UserRequestSchema(BaseSchema):
    email: EmailStr
    username: str
    password: str


class UserResponseSchema(BaseSchema):
    id: int
    email: EmailStr
    username: str
    posts: list[PostResponseSchema]
    created_at: datetime
    updated_at: datetime
