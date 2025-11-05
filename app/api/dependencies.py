"""FastAPI dependency declarations."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.orchestrator.factory import build_orchestrator
from app.orchestrator.orchestrator import TaskOrchestrator

_security = HTTPBearer()


def require_token(credentials: HTTPAuthorizationCredentials = Depends(_security)) -> None:
    settings = get_settings()
    token = credentials.credentials if credentials else None
    if not token or token != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_orchestrator() -> TaskOrchestrator:
    return build_orchestrator()


def get_settings_dependency():
    return get_settings()
