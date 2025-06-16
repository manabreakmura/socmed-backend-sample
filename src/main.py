from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.db import create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)
