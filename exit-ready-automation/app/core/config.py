"""
Application configuration using Pydantic Settings.
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="Exit Ready Automation", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    # Database - Exit Ready
    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/exit_ready",
        alias="DATABASE_URL"
    )

    # Database - CRM Core (read-only)
    crm_database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/indiestack",
        alias="CRM_DATABASE_URL"
    )

    # Database Connection Pool
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, alias="DB_POOL_RECYCLE")

    # Valuation Engine
    valuation_engine_base_url: str = Field(
        default="https://api.capitallink.com/valuation/v1",
        alias="VALUATION_ENGINE_BASE_URL"
    )
    valuation_engine_api_key: str = Field(
        default="",
        alias="VALUATION_ENGINE_API_KEY"
    )
    valuation_engine_timeout: int = Field(default=30, alias="VALUATION_ENGINE_TIMEOUT")
    valuation_engine_stub_mode: bool = Field(default=True, alias="VALUATION_ENGINE_STUB_MODE")

    # Email Engine
    email_engine_base_url: str = Field(
        default="https://api.capitallink.com/email/v1",
        alias="EMAIL_ENGINE_BASE_URL"
    )
    email_engine_api_key: str = Field(default="", alias="EMAIL_ENGINE_API_KEY")
    email_engine_timeout: int = Field(default=30, alias="EMAIL_ENGINE_TIMEOUT")
    email_engine_stub_mode: bool = Field(default=True, alias="EMAIL_ENGINE_STUB_MODE")

    # File Storage
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    storage_base_path: str = Field(default="./storage", alias="STORAGE_BASE_PATH")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_bucket_name: Optional[str] = Field(default=None, alias="AWS_BUCKET_NAME")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")

    # Intake Form
    intake_form_base_url: str = Field(
        default="https://forms.capitallink.com/exit-ready",
        alias="INTAKE_FORM_BASE_URL"
    )
    intake_form_ttl_days: int = Field(default=30, alias="INTAKE_FORM_TTL_DAYS")

    # PDF Generation
    pdf_engine: str = Field(default="weasyprint", alias="PDF_ENGINE")
    pdf_template_dir: str = Field(default="./config/templates", alias="PDF_TEMPLATE_DIR")

    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    api_key: str = Field(default="", alias="API_KEY")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], alias="CORS_ALLOW_HEADERS")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    sentry_environment: str = Field(default="development", alias="SENTRY_ENVIRONMENT")

    # Feature Flags
    enable_auto_valuation: bool = Field(default=False, alias="ENABLE_AUTO_VALUATION")
    enable_gpt_drafts: bool = Field(default=False, alias="ENABLE_GPT_DRAFTS")
    gpt_api_key: Optional[str] = Field(default=None, alias="GPT_API_KEY")
    gpt_model: str = Field(default="gpt-4-turbo-preview", alias="GPT_MODEL")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        """Parse CORS methods from comma-separated string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        """Parse CORS headers from comma-separated string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


# Global settings instance
settings = Settings()
