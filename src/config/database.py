from decouple import config
from sqlalchemy import URL
from sqlmodel import Session, SQLModel, create_engine

from users.models import User

url_object = URL.create(
    drivername="postgresql",
    username=config("POSTGRES_USER"),
    password=config("POSTGRES_PASSWORD"),
    host=config("POSTGRES_HOST"),
    port=config("POSTGRES_PORT"),
    database=config("POSTGRES_DATABASE"),
)
engine = create_engine(url_object, echo=True)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
