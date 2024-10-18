from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from users.routers import router as user_router

app = FastAPI()
app.include_router(user_router)


@app.get("/")
async def root():
    return RedirectResponse("/docs")
