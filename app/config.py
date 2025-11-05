"""Application configuration management built on Pydantic settings."""

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Centralized configuration for the three-layer AI system."""

    api_host: str = Field("0.0.0.0", description="FastAPI binding host")
    api_port: int = Field(8000, description="FastAPI binding port")
    api_token: str = Field(
        "change-me",
        description="Bearer token for authenticating API/UI interactions.",
    )

    database_url: str = Field(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/lewis",
        description="SQLAlchemy connection string for PostgreSQL + pgvector.",
    )
    enable_db_echo: bool = Field(
        False, description="Toggle SQL echo for debugging SQLAlchemy sessions."
    )

    redis_url: str = Field(
        "redis://localhost:6379/0", description="Redis connection URI for queues."
    )
    redis_dlq_url: Optional[str] = Field(
        None, description="Optional Redis URI for dead-letter queue separation."
    )

    otlp_endpoint: Optional[str] = Field(
        None,
        description="OTLP endpoint for exporting OpenTelemetry traces/metrics.",
    )
    log_level: str = Field(
        "INFO",
        description="Application log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )

    s3_endpoint_url: Optional[str] = Field(
        None, description="Endpoint URL for MinIO/S3 compatible storage."
    )
    s3_region: str = Field("us-east-1", description="S3 region for object storage.")
    s3_access_key: Optional[str] = Field(
        None, description="Access key for MinIO/S3 object storage."
    )
    s3_secret_key: Optional[str] = Field(
        None, description="Secret key for MinIO/S3 object storage."
    )
    s3_bucket: str = Field(
        "agent-artifacts",
        description="Default bucket for storing orchestrator and agent artifacts.",
    )

    default_llm_provider: str = Field(
        "openai", description="Default provider name used by the LLM proxy."
    )
    openai_api_key: Optional[str] = Field(
        None, description="API key for OpenAI endpoints."
    )
    anthropic_api_key: Optional[str] = Field(
        None, description="API key for Anthropic (Claude) endpoints."
    )
    gemini_api_key: Optional[str] = Field(
        None, description="API key for Google Gemini endpoints."
    )

    sandbox_timeout_seconds: int = Field(
        30, description="Execution timeout for sandboxed code invocation."
    )
    sandbox_python: str = Field(
        "python", description="Python executable used for sandbox subprocess."
    )

    environment: str = Field(
        "development",
        description="Runtime environment name (development/staging/production).",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("api_token")
    def validate_api_token(cls, value: str) -> str:
        """Ensure API token is not left at its placeholder value."""
        if not value or value == "change-me":
            return value
        return value.strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()


def reset_settings_cache() -> None:
    """Reset cached settings (useful for tests)."""
    global settings
    get_settings.cache_clear()
    settings = get_settings()
