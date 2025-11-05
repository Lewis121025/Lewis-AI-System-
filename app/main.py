"""Entry point helpers for running the FastAPI application."""

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.infrastructure.db import get_engine, init_db
from app.infrastructure.telemetry import configure_logging, configure_tracing


def create_app() -> FastAPI:
    """Instantiate the FastAPI application."""
    configure_logging()
    app = FastAPI(
        title="Lewis AI System",
        version="0.1.0",
        description="Three-layer autonomous AI system backend.",
    )
    app.include_router(api_router)

    @app.on_event("startup")
    async def _startup_event() -> None:
        engine = get_engine()
        configure_tracing(app=app, engine=engine)
        try:
            init_db()
        except Exception as exc:  # pragma: no cover - startup failure
            app.logger.exception("Database initialization failed: %s", exc)  # type: ignore[attr-defined]

    return app


app = create_app()
