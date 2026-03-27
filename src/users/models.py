from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    email: str = Field(index=True, max_length=64, unique=True)
    username: str = Field(index=True, max_length=32, unique=True)
    hashed_password: str = Field(max_length=128)
