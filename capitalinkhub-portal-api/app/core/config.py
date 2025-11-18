"""
Application configuration using Pydantic settings.
All environment variables are loaded from .env file.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Main application settings.

    All values can be overridden via environment variables.
    """

    # Application
    PORTAL_ENV: str = Field(default="dev", description="Environment: dev, staging, prod")
    PORTAL_DEBUG: bool = Field(default=True, description="Enable debug mode")
    PORTAL_VERSION: str = Field(default="0.1.0", description="API version")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Security - API Keys
    PORTAL_API_KEY: str = Field(description="Primary API key for authentication")
    PORTAL_API_KEYS: str = Field(default="", description="Comma-separated list of additional API keys")

    # Database - IndieStack CRM
    INDIE_DB_DSN: str = Field(
        description="PostgreSQL DSN for IndieStack CRM (postgresql+asyncpg://user:pass@host:port/dbname)"
    )
    DB_ECHO: bool = Field(default=False, description="SQLAlchemy echo SQL queries")
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")

    # Integration URLs (optional, for future use)
    ENGAGEMENT_TRACKER_BASE_URL: str = Field(
        default="",
        description="Base URL for Indie Engagement Tracker API"
    )
    MATCHING_ENGINE_BASE_URL: str = Field(
        default="",
        description="Base URL for Indie Matching Engine API"
    )
    ENGAGEMENT_TRACKER_API_KEY: str = Field(default="", description="API key for engagement tracker")
    MATCHING_ENGINE_API_KEY: str = Field(default="", description="API key for matching engine")

    # Resources configuration
    PORTAL_RESOURCES_CONFIG_PATH: str = Field(
        default="config/resources.yaml",
        description="Path to resources configuration file"
    )

    # CORS (if needed for future browser access)
    CORS_ORIGINS: str = Field(default="", description="Comma-separated list of CORS origins")

    # Pagination defaults
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size for listings")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size for listings")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("PORTAL_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Validate environment value."""
        allowed = {"dev", "staging", "prod"}
        if v not in allowed:
            raise ValueError(f"PORTAL_ENV must be one of {allowed}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v_upper

    def get_all_api_keys(self) -> List[str]:
        """
        Get all valid API keys (primary + additional).

        Returns:
            List of API keys
        """
        keys = [self.PORTAL_API_KEY]
        if self.PORTAL_API_KEYS:
            additional = [k.strip() for k in self.PORTAL_API_KEYS.split(",") if k.strip()]
            keys.extend(additional)
        return keys

    def get_cors_origins(self) -> List[str]:
        """
        Get CORS origins as a list.

        Returns:
            List of CORS origin URLs
        """
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.PORTAL_ENV == "prod"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.PORTAL_ENV == "dev"


# Global settings instance
settings = Settings()
