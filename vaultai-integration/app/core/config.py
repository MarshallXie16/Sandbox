"""
VaultAI Integration Layer - Configuration Module
Centralized settings management using Pydantic Settings.
"""

from typing import List, Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All sensitive data must be provided via .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================================
    # General Settings
    # ========================================
    VAULTAI_ENV: Literal["dev", "staging", "prod"] = "dev"
    VAULTAI_DEBUG: bool = False
    VAULTAI_API_KEYS: str = Field(
        default="",
        description="Comma-separated list of valid API keys for internal auth",
    )
    VAULTAI_HOST: str = "0.0.0.0"
    VAULTAI_PORT: int = 8010

    # ========================================
    # Database Configuration
    # ========================================
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://vaultai_user:vaultai_password@localhost:5432/vaultai_db",
        description="Async PostgreSQL connection string",
    )

    # ========================================
    # LLM Provider Configuration
    # ========================================
    LLM_DEFAULT_PROVIDER: Literal["local", "openai_compatible", "azure"] = "local"

    # Local Private LLM
    LLM_LOCAL_BASE_URL: str = "http://localhost:8009"
    LLM_LOCAL_MODEL: str = "llama3-70b-instruct"
    LLM_LOCAL_API_KEY: Optional[str] = None

    # OpenAI Compatible
    LLM_OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_OPENAI_API_KEY: Optional[str] = None
    LLM_OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Azure OpenAI (Optional)
    LLM_AZURE_BASE_URL: Optional[str] = None
    LLM_AZURE_API_KEY: Optional[str] = None
    LLM_AZURE_MODEL: Optional[str] = None
    LLM_AZURE_API_VERSION: str = "2024-02-01"

    # Request Settings
    LLM_TIMEOUT_SECONDS: int = 60
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_RETRIES: int = 3

    # ========================================
    # Embeddings Configuration
    # ========================================
    USE_EMBEDDINGS: bool = True
    EMBEDDINGS_PROVIDER: Literal["local", "openai_compatible"] = "local"
    EMBEDDINGS_MODEL: str = "text-embedding-ada-002"
    EMBEDDINGS_DIMENSION: int = 1536

    # ========================================
    # Security & Redaction
    # ========================================
    ENABLE_PII_REDACTION: bool = True
    REDACTION_PATTERNS: str = "ssn,email,phone,credit_card"

    # ========================================
    # Rate Limiting
    # ========================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    # ========================================
    # Logging
    # ========================================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"
    LOG_REQUESTS: bool = True
    LOG_RESPONSES: bool = False

    # ========================================
    # CORS Configuration
    # ========================================
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True

    # ========================================
    # Feature Flags
    # ========================================
    ENABLE_UI: bool = True
    ENABLE_VECTOR_SEARCH: bool = True
    ENABLE_PROMPT_VERSIONING: bool = True

    # ========================================
    # Computed Properties
    # ========================================
    @property
    def api_keys_list(self) -> List[str]:
        """Parse comma-separated API keys into a list."""
        if not self.VAULTAI_API_KEYS:
            return []
        return [key.strip() for key in self.VAULTAI_API_KEYS.split(",") if key.strip()]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def redaction_patterns_list(self) -> List[str]:
        """Parse comma-separated redaction patterns into a list."""
        return [
            pattern.strip()
            for pattern in self.REDACTION_PATTERNS.split(",")
            if pattern.strip()
        ]

    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0")
        return v

    @field_validator("LLM_MAX_TOKENS")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Ensure max tokens is reasonable."""
        if v < 1 or v > 32000:
            raise ValueError("LLM_MAX_TOKENS must be between 1 and 32000")
        return v

    def get_llm_config(self, provider: Optional[str] = None) -> dict:
        """
        Get LLM configuration for a specific provider.

        Args:
            provider: Provider name (local, openai_compatible, azure).
                     If None, uses default provider.

        Returns:
            Dictionary with provider configuration.
        """
        provider = provider or self.LLM_DEFAULT_PROVIDER

        if provider == "local":
            return {
                "base_url": self.LLM_LOCAL_BASE_URL,
                "model": self.LLM_LOCAL_MODEL,
                "api_key": self.LLM_LOCAL_API_KEY,
                "timeout": self.LLM_TIMEOUT_SECONDS,
                "max_tokens": self.LLM_MAX_TOKENS,
                "temperature": self.LLM_TEMPERATURE,
            }
        elif provider == "openai_compatible":
            return {
                "base_url": self.LLM_OPENAI_BASE_URL,
                "model": self.LLM_OPENAI_MODEL,
                "api_key": self.LLM_OPENAI_API_KEY,
                "timeout": self.LLM_TIMEOUT_SECONDS,
                "max_tokens": self.LLM_MAX_TOKENS,
                "temperature": self.LLM_TEMPERATURE,
            }
        elif provider == "azure":
            return {
                "base_url": self.LLM_AZURE_BASE_URL,
                "model": self.LLM_AZURE_MODEL,
                "api_key": self.LLM_AZURE_API_KEY,
                "api_version": self.LLM_AZURE_API_VERSION,
                "timeout": self.LLM_TIMEOUT_SECONDS,
                "max_tokens": self.LLM_MAX_TOKENS,
                "temperature": self.LLM_TEMPERATURE,
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Global settings instance
settings = Settings()
