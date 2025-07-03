# backend/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core paths
    CHROMA_DB_DIR: str = "/app/chroma_index"

    # Database
    DATABASE_URL: str

    # MinIO / S3
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    # Redis / Elasticsearch
    REDIS_URL: str
    ELASTICSEARCH_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str

    # Optional
    APP_ENV: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


settings = Settings()
