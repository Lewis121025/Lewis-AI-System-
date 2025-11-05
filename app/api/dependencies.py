"""FastAPI 依赖声明模块，集中定义鉴权及对象单例。"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.orchestrator.factory import build_orchestrator
from app.orchestrator.orchestrator import TaskOrchestrator

_security = HTTPBearer()


def require_token(credentials: HTTPAuthorizationCredentials = Depends(_security)) -> None:
    """校验 Bearer Token，确保只有持有令牌的请求才能继续。"""
    settings = get_settings()
    token = credentials.credentials if credentials else None
    if not token or token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_orchestrator() -> TaskOrchestrator:
    """返回单例编排器，供路由层注入使用。"""
    return build_orchestrator()


def get_settings_dependency():
    """提供 Settings 依赖，方便在路由中直接读取配置。"""
    return get_settings()
