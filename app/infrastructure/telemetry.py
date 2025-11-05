"""可观测性工具：统一配置结构化日志与 OpenTelemetry 追踪。"""

from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Optional

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from pythonjsonlogger import jsonlogger

try:  # OTLP exporter位置在 1.18+ 中变更
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )
except ImportError:  # pragma: no cover - 兼容旧版本
    from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter  # type: ignore

from app.config import get_settings

LOGGER = logging.getLogger(__name__)
_LOGGING_CONFIGURED = False
_TRACING_CONFIGURED = False


def configure_logging(level: Optional[str] = None) -> None:
    """Configure structured logging for the application."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    settings = get_settings()
    log_level = (level or settings.log_level).upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "()": jsonlogger.JsonFormatter,
                    "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                }
            },
            "root": {"handlers": ["default"], "level": log_level},
        }
    )
    _LOGGING_CONFIGURED = True


def configure_tracing(app=None, engine=None) -> None:
    """Wire up OpenTelemetry tracing for FastAPI and SQLAlchemy."""
    global _TRACING_CONFIGURED
    if _TRACING_CONFIGURED:
        return

    settings = get_settings()
    resource = Resource.create({"service.name": "lewis-ai-system"})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    if settings.otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint)
    else:
        exporter = ConsoleSpanExporter()

    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)

    if app is not None:
        FastAPIInstrumentor.instrument_app(app)

    if engine is not None:
        SQLAlchemyInstrumentor().instrument(
            engine=engine, enable_commenter=True, commenter_options={}
        )

    _TRACING_CONFIGURED = True
