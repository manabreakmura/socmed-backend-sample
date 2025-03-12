from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from config.database import create_database
from routers.auth import auth_router
from routers.users import users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return RedirectResponse("/docs")
