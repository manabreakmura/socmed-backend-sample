from os import environ

from dotenv import load_dotenv
from sqlalchemy import URL
from sqlmodel import Session, SQLModel, create_engine

from users.models import User

load_dotenv()


url_object = URL.create(
    drivername="postgresql",
    username=environ["POSTGRES_USER"],
    password=environ["POSTGRES_PASSWORD"],
    host=environ["POSTGRES_HOST"],
    port=environ["POSTGRES_PORT"],
    database=environ["POSTGRES_DATABASE"],
)
engine = create_engine(url_object, echo=True)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
