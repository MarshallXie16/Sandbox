"""Application configuration loaded from environment variables."""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8001, alias="API_PORT")
    api_secret_key: str = Field(default="change-me-in-production", alias="API_SECRET_KEY")

    # Engagement Tracker Database
    database_url: str = Field(
        default="sqlite:///./engagement_tracker.db",
        alias="DATABASE_URL",
    )

    # IndieStack CRM Core Integration
    indie_crm_db_url: Optional[str] = Field(default=None, alias="INDIE_CRM_DB_URL")
    indie_crm_api_url: Optional[str] = Field(default=None, alias="INDIE_CRM_API_URL")
    indie_crm_api_key: Optional[str] = Field(default=None, alias="INDIE_CRM_API_KEY")

    # Capital Ink Hub Email Engine Integration
    email_engine_db_url: Optional[str] = Field(default=None, alias="EMAIL_ENGINE_DB_URL")

    # Optional Future Integrations
    hubspot_api_key: Optional[str] = Field(default=None, alias="HUBSPOT_API_KEY")
    sendy_api_url: Optional[str] = Field(default=None, alias="SENDY_API_URL")
    sendy_api_key: Optional[str] = Field(default=None, alias="SENDY_API_KEY")

    # Scoring Configuration
    default_scoring_profile_id: int = Field(default=1, alias="DEFAULT_SCORING_PROFILE_ID")
    score_decay_enabled: bool = Field(default=True, alias="SCORE_DECAY_ENABLED")
    score_decay_days: int = Field(default=90, alias="SCORE_DECAY_DAYS")
    score_decay_factor: float = Field(default=0.5, alias="SCORE_DECAY_FACTOR")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


# Global settings instance
settings = Settings()
