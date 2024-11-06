from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, unique=True, index=True)
    email: EmailStr = Field(max_length=64, unique=True, index=True)
    password: str = Field(max_length=128)
    is_admin: bool = False


class Token(SQLModel):
    access_token: str
    token_type: str
