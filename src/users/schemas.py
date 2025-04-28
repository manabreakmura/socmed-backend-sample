from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRequestSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    updated_at: datetime
