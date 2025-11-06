# src/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
from pathlib import Path
class Settings(BaseSettings):


    # General
    APP_NAME: str = "Huda AI Backend"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # could be: development | staging | production
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    #  Server 
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    

    # BASE URLS
    BASE_DB_URL: str = "postgresql+psycopg2://postgres:231220@localhost:5432/huda_ai"
    
    #  Paths 
    LOG_DIR: str = "logs"

    #  Security 
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unknown env vars
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader so .env is parsed only once.
    You can safely import and call get_settings() anywhere.
    """
    return Settings()
