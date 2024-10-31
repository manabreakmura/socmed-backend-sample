from decouple import config
from sqlalchemy import URL
from sqlmodel import Session, create_engine

from users.models import User

database_url = URL.create(
    "postgresql+psycopg",
    username=config("POSTGRES_USERNAME"),
    password=config("POSTGRES_PASSWORD"),
    host=config("POSTGRES_HOST"),
    database=config("POSTGRES_DATABASE"),
)

engine = create_engine(database_url)


def get_session():
    with Session(engine) as session:
        yield session
