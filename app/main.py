"""FastAPI 应用入口模块。

负责创建并初始化整个后端服务，包括：
- 配置日志与 OpenTelemetry；
- 建立数据库连接并确保数据表存在；
- 注册所有 API 路由。
"""

import logging

from fastapi import FastAPI

from app.api.routes import router as api_router
from app.infrastructure.db import get_engine, init_db
from app.infrastructure.telemetry import configure_logging, configure_tracing


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例，并在启动时完成必要的初始化。"""
    configure_logging()
    app = FastAPI(
        title="Lewis AI System",
        version="0.1.0",
        description="Three-layer autonomous AI system backend.",
    )
    app.state.logger = logging.getLogger("uvicorn.error")
    app.include_router(api_router)

    @app.on_event("startup")
    async def _startup_event() -> None:
        """启动事件：配置追踪并初始化数据库。

        这里单独放在 startup 钩子中，可以避免在导入阶段执行
        外部副作用，便于单元测试与脚本复用。
        """
        engine = get_engine()
        configure_tracing(app=app, engine=engine)
        try:
            init_db()
        except Exception as exc:  # pragma: no cover - startup failure
            app.state.logger.exception("Database initialization failed: %s", exc)

    return app


app = create_app()
