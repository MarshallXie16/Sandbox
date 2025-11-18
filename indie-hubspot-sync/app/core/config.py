"""
Core configuration module for HubSpot-IndieStack sync service.
Loads environment variables and provides app-wide configuration.
"""

from typing import Literal, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # HubSpot Configuration
    hubspot_private_app_token: str = Field(..., alias="HUBSPOT_PRIVATE_APP_TOKEN")

    # IndieStack Database Configuration
    indie_db_host: str = Field(default="localhost", alias="INDIE_DB_HOST")
    indie_db_port: int = Field(default=5432, alias="INDIE_DB_PORT")
    indie_db_name: str = Field(default="indie_crm", alias="INDIE_DB_NAME")
    indie_db_user: str = Field(default="indie_user", alias="INDIE_DB_USER")
    indie_db_password: str = Field(default="", alias="INDIE_DB_PASSWORD")

    # IndieStack API Configuration (future)
    indie_api_url: Optional[str] = Field(default=None, alias="INDIE_API_URL")
    indie_api_key: Optional[str] = Field(default=None, alias="INDIE_API_KEY")

    # Integration Mode
    indie_integration_mode: Literal["database", "api"] = Field(
        default="database", alias="INDIE_INTEGRATION_MODE"
    )

    # Local Tracking Database
    sync_db_url: str = Field(
        default="sqlite:///./sync_tracking.db", alias="SYNC_DB_URL"
    )

    # Sync Configuration
    default_sync_direction: Literal[
        "indie_to_hubspot", "hubspot_to_indie", "bidirectional"
    ] = Field(default="bidirectional", alias="DEFAULT_SYNC_DIRECTION")

    sync_batch_size: int = Field(default=100, alias="SYNC_BATCH_SIZE")

    sync_conflict_resolution: Literal[
        "indie_wins", "hubspot_wins", "newest_wins"
    ] = Field(default="indie_wins", alias="SYNC_CONFLICT_RESOLUTION")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: Literal["json", "text"] = Field(default="json", alias="LOG_FORMAT")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=False, alias="API_RELOAD")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def indie_db_dsn(self) -> str:
        """Construct PostgreSQL DSN for IndieStack database."""
        return (
            f"postgresql://{self.indie_db_user}:{self.indie_db_password}"
            f"@{self.indie_db_host}:{self.indie_db_port}/{self.indie_db_name}"
        )


# Global settings instance
settings = Settings()
