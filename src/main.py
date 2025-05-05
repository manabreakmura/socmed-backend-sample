from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config.db import create_db_tables
from posts.routers import posts_router
from users.routers import auth_router, users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(posts_router)


@app.get("/")
async def root():
    return RedirectResponse("/docs")
