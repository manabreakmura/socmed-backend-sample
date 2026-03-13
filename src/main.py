from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings

app = FastAPI(
    debug=settings.DEBUG,
    docs_url="/docs" if settings.DEBUG else None,
)

origins = [URL for URL in settings.FRONTEND_URL.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
