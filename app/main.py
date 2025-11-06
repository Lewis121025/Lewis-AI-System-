"""FastAPI 应用入口模块。

负责创建并初始化整个后端服务，包括：
- 配置日志与 OpenTelemetry；
- 建立数据库连接并确保数据表存在；
- 注册所有 API 路由。
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.infrastructure.db import get_engine, init_db
from app.infrastructure.telemetry import configure_logging, configure_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理：启动时初始化，关闭时清理资源。

    使用 lifespan 替代已废弃的 on_event，提供更好的资源管理。
    """
    # 启动逻辑
    engine = get_engine()
    configure_tracing(app=app, engine=engine)
    try:
        init_db()
        app.state.logger.info("Database initialized successfully")
    except Exception as exc:  # pragma: no cover - startup failure
        app.state.logger.exception("Database initialization failed: %s", exc)

    yield

    # 关闭逻辑（如需清理资源可在此添加）
    app.state.logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例，并在启动时完成必要的初始化。"""
    configure_logging()
    app = FastAPI(
        title="Lewis AI System",
        version="0.1.0",
        description="Three-layer autonomous AI system backend.",
        lifespan=lifespan,
    )
    app.state.logger = logging.getLogger("uvicorn.error")
    app.include_router(api_router)

    return app


app = create_app()
