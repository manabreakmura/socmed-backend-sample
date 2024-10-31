from decouple import config
from sqlalchemy import URL
from sqlmodel import Session, SQLModel, create_engine

database_url = URL.create(
    "postgresql+psycopg",
    username=config("POSTGRES_USERNAME"),
    password=config("POSTGRES_PASSWORD"),
    host=config("POSTGRES_HOST"),
    database=config("POSTGRES_DATABASE"),
)

engine = create_engine(database_url)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
