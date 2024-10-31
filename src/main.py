from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from config.database import engine
from users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
