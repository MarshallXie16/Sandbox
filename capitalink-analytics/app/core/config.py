"""Application configuration and settings."""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    analytics_env: str = Field(default="dev", description="Environment: dev, staging, prod")
    analytics_debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Security
    analytics_api_keys: str = Field(
        default="",
        description="Comma-separated API keys for authentication",
    )

    # Analytics Database (this module's own schema)
    analytics_database_url: str = Field(
        ...,
        description="PostgreSQL DSN for analytics database",
    )

    # Upstream Module Databases (read-only)
    crm_database_url: Optional[str] = Field(
        default=None,
        description="CRM database DSN (read-only)",
    )
    exit_ready_database_url: Optional[str] = Field(
        default=None,
        description="Exit Ready database DSN (read-only)",
    )
    facilitator_database_url: Optional[str] = Field(
        default=None,
        description="Facilitator database DSN (read-only)",
    )
    match_engine_database_url: Optional[str] = Field(
        default=None,
        description="Match Engine database DSN (read-only)",
    )
    engagement_database_url: Optional[str] = Field(
        default=None,
        description="Engagement Tracker database DSN (read-only)",
    )
    portal_database_url: Optional[str] = Field(
        default=None,
        description="Portal API database DSN (read-only)",
    )

    # Server Configuration
    analytics_host: str = Field(default="0.0.0.0", description="Server host")
    analytics_port: int = Field(default=8008, description="Server port")
    analytics_workers: int = Field(default=4, description="Number of workers")

    # CORS
    analytics_cors_origins: str = Field(
        default="",
        description="Comma-separated CORS origins",
    )

    @field_validator("analytics_api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: str) -> str:
        """Validate API keys are provided."""
        if not v or not v.strip():
            raise ValueError("At least one API key must be configured")
        return v

    def get_api_keys(self) -> List[str]:
        """Get list of valid API keys."""
        return [key.strip() for key in self.analytics_api_keys.split(",") if key.strip()]

    def get_cors_origins(self) -> List[str]:
        """Get list of CORS origins."""
        if not self.analytics_cors_origins:
            return []
        return [
            origin.strip()
            for origin in self.analytics_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.analytics_env.lower() in ("dev", "development")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.analytics_env.lower() in ("prod", "production")


# Global settings instance
settings = Settings()
