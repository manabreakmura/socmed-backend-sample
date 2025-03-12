from typing import Annotated

from decouple import config
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from models import users

engine = create_engine(config("DATABASE_URL"))


def create_database():
    return SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


session_dependency = Annotated[Session, Depends(get_session)]
