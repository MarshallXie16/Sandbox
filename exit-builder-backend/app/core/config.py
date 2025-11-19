"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/exit_builder"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Capital Link Exit Builder"
    VERSION: str = "1.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
