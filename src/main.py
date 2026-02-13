from contextlib import asynccontextmanager

from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.routers import auth_router
from config.db import create_db_tables
from posts.routers import posts_router
from users.routers import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    yield


app = FastAPI(lifespan=lifespan)

origins = [URL for URL in config("FRONTEND_URL").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(users_router)
