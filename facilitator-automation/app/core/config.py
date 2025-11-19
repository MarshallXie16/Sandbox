"""
Configuration management for Facilitator Automation module.
Uses Pydantic Settings for environment variable validation and type safety.
"""

from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Environment
    facilitator_env: str = Field(default="dev", description="Environment: dev, staging, prod")
    facilitator_debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Security
    facilitator_api_keys: str = Field(
        default="",
        description="Comma-separated API keys for authentication"
    )

    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL for Facilitator database"
    )

    # CRM Integration
    crm_database_url: str = Field(
        default="",
        description="PostgreSQL connection URL for CRM database"
    )
    crm_api_base_url: str = Field(
        default="http://localhost:8001/api/v1",
        description="CRM API base URL"
    )
    crm_api_key: str = Field(
        default="",
        description="CRM API key"
    )

    # Matching Engine Integration
    match_engine_base_url: str = Field(
        default="http://localhost:8002/api/v1",
        description="Matching Engine API base URL"
    )
    match_engine_api_key: str = Field(
        default="",
        description="Matching Engine API key"
    )
    match_engine_stub_mode: bool = Field(
        default=True,
        description="Use stub mode for Matching Engine (for testing)"
    )

    # Email Engine Integration
    email_engine_base_url: str = Field(
        default="http://localhost:8003/api/v1",
        description="Email Engine API base URL"
    )
    email_engine_api_key: str = Field(
        default="",
        description="Email Engine API key"
    )
    email_engine_stub_mode: bool = Field(
        default=True,
        description="Use stub mode for Email Engine (for testing)"
    )

    # Fee Configuration
    default_offer_fee_fixed: float = Field(
        default=5000.0,
        description="Default fixed fee at offer stage"
    )
    default_success_fee_rate: float = Field(
        default=0.05,
        description="Default success fee rate (0.05 = 5%)"
    )
    default_currency: str = Field(
        default="CAD",
        description="Default currency"
    )

    # API Server
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8080, description="API server port")
    api_reload: bool = Field(default=False, description="Auto-reload on code changes")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: str = Field(default="*")
    cors_allow_headers: str = Field(default="*")

    @validator("facilitator_api_keys")
    def parse_api_keys(cls, v: str) -> List[str]:
        """Parse comma-separated API keys into list."""
        if not v:
            return []
        return [key.strip() for key in v.split(",") if key.strip()]

    @validator("cors_origins")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into list."""
        if not v:
            return []
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @validator("default_success_fee_rate")
    def validate_success_fee_rate(cls, v: float) -> float:
        """Ensure success fee rate is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Success fee rate must be between 0 and 1")
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.facilitator_env.lower() == "prod"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.facilitator_env.lower() == "dev"


# Global settings instance
settings = Settings()
