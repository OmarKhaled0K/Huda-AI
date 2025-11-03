# src/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
from pathlib import Path
class Settings(BaseSettings):


    # General
    APP_NAME: str = "Huda AI"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # could be: development | staging | production
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    #  Server 
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    

    # BASE URLS
    BASE_QURAN_AUDIO_URL: str = "https://quranapi.pages.dev/api/audio"
    BASE_QURAN_TEXT_URL: str = "https://api.alquran.cloud/v1"
    BASE_QDRANT_URL: str = "http://qdrant:6333"

    #  OpenAI / LLM
    LLM_PROVIDER: str = "openai"  # could be: openai | llama | deepseek 
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"
    LLM_TEMPERATURE: float = 0.5
    LLM_MAX_TOKENS: int = 512
    LLAMA_MODEL: str = "llama-3.1"
    REASONING_ENABLED: bool = False
    REASONING_CHAIN_STEPS: int = 3

    #  Vector DB 
    VECTOR_DB_URL: Optional[str] = None
    VECTOR_DB_API_KEY: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = "RW3nKzxeY1mPlokNZaWB9PCr5KpooA9AN4Z0YyCb64o487Saf72kHuzBY1F6DeGK"

    # Embedding
    DEFAULT_VECTOR_SIZE: int = 1536
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEFAULT_DISTANCE: str = "Cosine"  # could be: Cosine | Euclidean | Dot

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
