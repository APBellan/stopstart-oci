from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Geral
    APP_NAME: str = "StopStart OCI"
    APP_ENV: str = "development"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Banco (vamos usar isso depois no SQLAlchemy)
    DATABASE_URL: str = "postgresql+psycopg2://stopstart:stopstart@db:5432/stopstart"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
