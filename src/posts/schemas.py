from datetime import datetime

from pydantic import BaseModel


class PostRequestSchema(BaseModel):
    title: str
    body: str


class PostResponseSchema(BaseModel):
    id: int
    title: str
    body: str
    user_id: int
    created_at: datetime
    updated_at: datetime
