"""应用配置管理模块（基于 Pydantic Settings）。

This module centralises runtime configuration for the three-layer AI system.
同时提供中文注释，便于快速理解各字段的用途。
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, validator

try:
    # Pydantic v2 style configuration (optional dependency).
    from pydantic_settings import BaseSettings  # type: ignore
except ModuleNotFoundError:
    # Fallback for Pydantic v1 environments where BaseSettings lives in pydantic.
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """三层智能系统的集中配置。

    各字段可以通过环境变量或 `.env` 文件覆盖，具体说明如下：
    - api_host / api_port：FastAPI 服务监听的地址与端口。
    - api_token：对外暴露接口的访问令牌，用于简单鉴权。
    - database_url：PostgreSQL（或 SQLite 等）连接串，需支持 pgvector。
    - redis_url：Redis 任务队列连接地址。
    - openrouter/openai 等密钥：供 LLMProxy 路由调用。
    - sandbox_*：沙箱执行的基础配置，如超时时间、Python 解释器等。
    """

    api_host: str = Field("127.0.0.1", description="FastAPI binding host")
    api_port: int = Field(8002, description="FastAPI binding port")
    api_token: str = Field(
        "change-me",
        description=(
            "Bearer token for authenticating API/UI interactions. "
            "接口访问令牌，生产环境请务必替换。"
        ),
    )

    database_url: str = Field(
        "postgresql+psycopg2://postgres:postgres@localhost:5432/lewis",
        description="SQLAlchemy connection string for PostgreSQL + pgvector. PostgreSQL 连接 URL。",
    )
    enable_db_echo: bool = Field(
        False, description="Toggle SQL echo for debugging SQLAlchemy sessions."
    )

    redis_url: Optional[str] = Field(
        None, description="Redis connection URI for queues. Set to None to disable Redis."
    )
    redis_dlq_url: Optional[str] = Field(
        None, description="Optional Redis URI for dead-letter queue separation."
    )

    otlp_endpoint: Optional[str] = Field(
        None,
        description="OTLP endpoint for exporting OpenTelemetry traces/metrics. 遥测数据上报地址。",
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
    openrouter_api_key: Optional[str] = Field(
        None, description="API key for OpenRouter aggregation platform."
    )
    openrouter_base_url: str = Field(
        "https://openrouter.ai/api/v1",
        description="Base URL for OpenRouter API requests.",
    )
    openrouter_default_model: str = Field(
        "meta-llama/llama-4-maverick:free",
        description="Default OpenRouter model identifier.",
    )

    # Google Custom Search API configuration
    google_search_api_key: Optional[str] = Field(
        None, description="Google Custom Search API key for web search capabilities."
    )
    google_search_engine_id: Optional[str] = Field(
        None, description="Google Custom Search Engine ID (cx parameter)."
    )
    google_search_max_results: int = Field(
        5, description="Maximum number of search results to return."
    )
    
    # Weather API configuration
    weather_api_key: Optional[str] = Field(
        None, description="WeatherAPI.com API key for real-time weather data."
    )

    sandbox_timeout_seconds: int = Field(
        30, description="Execution timeout for sandboxed code invocation. 沙箱执行超时时间（秒）。"
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
        """确保 API Token 非空。若仍为默认值则返回原值并在文档提醒替换。"""
        if not value or value == "change-me":
            return value
        return value.strip()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """返回带缓存的配置实例，避免重复读取 .env/环境变量。"""
    return Settings()


settings = get_settings()


def reset_settings_cache() -> None:
    """重置配置缓存（测试场景常用，重新读取最新环境变量）。"""
    global settings
    get_settings.cache_clear()
    settings = get_settings()
