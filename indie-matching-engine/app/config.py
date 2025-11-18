"""
Configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional

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

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://localhost:5432/indie_crm_core",
        description="PostgreSQL database URL for CRM access",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8003, description="API port")
    api_reload: bool = Field(default=False, description="Enable auto-reload")
    api_workers: int = Field(default=1, description="Number of worker processes")

    # Authentication
    api_key: str = Field(
        default="development-key-change-in-production",
        description="API key for authentication",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # External Services
    engagement_tracker_url: Optional[str] = Field(
        default=None,
        description="URL for the engagement tracker service",
    )
    engagement_tracker_api_key: Optional[str] = Field(
        default=None,
        description="API key for engagement tracker",
    )

    # Scoring Configuration
    scoring_config_path: str = Field(
        default="config/scoring_rules.yaml",
        description="Path to scoring rules YAML file",
    )

    # Matching Engine Settings
    min_recommendation_score: float = Field(
        default=40.0,
        description="Minimum score for a recommendation",
    )
    max_recommendations: int = Field(
        default=20,
        description="Maximum number of recommendations to return",
    )
    cache_ttl_seconds: int = Field(
        default=3600,
        description="Cache TTL in seconds",
    )

    # Feature Flags
    enable_engagement_integration: bool = Field(
        default=False,
        description="Enable engagement tracker integration",
    )
    enable_match_caching: bool = Field(
        default=True,
        description="Enable match score caching",
    )
    enable_batch_scoring: bool = Field(
        default=True,
        description="Enable batch scoring operations",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
