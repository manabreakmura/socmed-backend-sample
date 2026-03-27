from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool
    DATABASE_URL: str
    CACHE_URL: str
    FRONTEND_URL: str
    ALGORITHM: str = "HS256"
    SECRET_KEY: str  # openssl rand -hex 32
    ACCESS_TOKEN_EXPIRE: int
    REFRESH_TOKEN_EXPIRE: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
