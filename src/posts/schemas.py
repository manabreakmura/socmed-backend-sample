from datetime import datetime

from config.db import BaseSchema


class PostRequestSchema(BaseSchema):
    title: str
    body: str


class PostResponseSchema(BaseSchema):
    id: int
    title: str
    body: str
    user_id: int
    created_at: datetime
    updated_at: datetime
