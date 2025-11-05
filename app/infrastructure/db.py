"""Database session management utilities."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.base import Base

_ENGINE: Optional[Engine] = None
_SESSION_FACTORY: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Return a singleton SQLAlchemy engine instance."""
    global _ENGINE
    if _ENGINE is None:
        settings = get_settings()
        _ENGINE = create_engine(
            settings.database_url,
            echo=settings.enable_db_echo,
            future=True,
        )
    return _ENGINE


def get_session_factory() -> sessionmaker:
    """Configure and cache the session factory."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        _SESSION_FACTORY = sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=Session,
        )
    return _SESSION_FACTORY


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional session scope."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(create_extensions: bool = True) -> None:
    """
    Initialize database schema and optional extensions.

    Parameters
    ----------
    create_extensions:
        Enable pgvector extension installation when using PostgreSQL.
    """
    engine = get_engine()
    if create_extensions and engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
