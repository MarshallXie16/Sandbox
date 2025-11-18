"""
Configuration management using Pydantic Settings.
All settings are loaded from environment variables with sensible defaults.
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    database_url: str = Field(default="sqlite:///./email_campaigns.db")

    # Sendy Configuration
    sendy_base_url: Optional[str] = Field(default=None)
    sendy_api_key: Optional[str] = Field(default=None)
    sendy_list_id: Optional[str] = Field(default=None)

    # SMTP Configuration
    smtp_host: Optional[str] = Field(default=None)
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_use_tls: bool = Field(default=True)
    smtp_from_name: str = Field(default="Capital Ink Hub")
    smtp_from_email: str = Field(default="noreply@capitalinkhub.com")

    # Rate Limiting Defaults
    default_max_per_hour: int = Field(default=100)
    default_max_per_day: int = Field(default=500)
    default_min_delay_seconds: int = Field(default=2)
    default_max_delay_seconds: int = Field(default=7)

    # IndieStack Integration
    indiestack_webhook_url: Optional[str] = Field(default=None)
    indiestack_api_key: Optional[str] = Field(default=None)

    # Application Settings
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/email_engine.log")
    environment: str = Field(default="development")

    def is_sendy_configured(self) -> bool:
        """Check if Sendy is properly configured."""
        return all([self.sendy_base_url, self.sendy_api_key])

    def is_smtp_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return all([self.smtp_host, self.smtp_username, self.smtp_password])

    def is_indiestack_webhook_configured(self) -> bool:
        """Check if IndieStack webhook is configured."""
        return self.indiestack_webhook_url is not None


# Global settings instance
settings = Settings()
