"""
Configuration module for Scrum AI Assistant.
Uses Pydantic Settings for environment variable management.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Scrum AI Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/scrum_db"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND_URL: str = "redis://redis:6379/1"

    # Jira
    JIRA_BASE_URL: str = "https://your-domain.atlassian.net"
    JIRA_API_TOKEN: str = "your-api-token"
    JIRA_USER_EMAIL: str = "user@example.com"

    # Azure Boards
    AZURE_BOARDS_ORG: str = "your-org"
    AZURE_BOARDS_PAT: str = "your-pat"
    AZURE_BOARDS_API_VERSION: str = "7.0"

    # Slack
    SLACK_WEBHOOK_URL: Optional[str] = None

    # File storage
    AUDIO_STORAGE_PATH: str = "/data/audio"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
