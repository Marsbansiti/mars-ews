from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "MARS NEWS"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "mars_news_development_secret_jwt_key_2026_secured"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite:///./mars_news.db"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_MASTER_KEY: str = "mars_master_search_key_12345"

    STORAGE_BACKEND: str = "local"
    STORAGE_DIR: str = "./media_uploads"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = "mars-news-media"
    R2_ACCOUNT_ID: Optional[str] = None

    EMERGENCY_PUBLISHING_PAUSE: bool = False
    AUTO_COLLECT_INTERVAL_MINUTES: int = 15
    AUTO_PUBLISH_DELAY_MINUTES: int = 5
    FACT_VALIDATION_STRICT_MODE: bool = True

    ADMIN_EMAIL: str = "admin@marsnews.in"
    ADMIN_PASSWORD: str = "MarsNewsSuperAdmin2026!"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
