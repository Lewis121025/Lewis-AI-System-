"""Database entities representing system state and experiences."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.models.base import Base, TableNameMixin
from app.models.enums import ExperienceKind, TaskStatus


class VectorType(TypeDecorator):
    """
    Database-agnostic vector column.

    Uses pgvector when available with PostgreSQL, otherwise falls back to JSON.
    """

    cache_ok = True

    def __init__(self, dimensions: int = 1536) -> None:
        super().__init__()
        self.dimensions = dimensions

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector  # type: ignore
            except Exception as exc:  # pragma: no cover - defensive
                raise RuntimeError(
                    "pgvector package is required for PostgreSQL usage."
                ) from exc
            return dialect.type_descriptor(Vector(self.dimensions))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return list(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return list(value)


class TaskRecord(Base, TableNameMixin):
    """High-level orchestrated task instance."""

    task_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False
    )
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    events: Mapped[list["TaskEventRecord"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", lazy="selectin"
    )


class TaskEventRecord(Base, TableNameMixin):
    """Chronological log of task progress and agent actions."""

    task_id: Mapped[int] = mapped_column(ForeignKey("task_record.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    task: Mapped[TaskRecord] = relationship(back_populates="events")


class ExperienceRecord(Base, TableNameMixin):
    """Experience cases stored for case-based reasoning."""

    reference_id: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[ExperienceKind] = mapped_column(
        Enum(ExperienceKind), default=ExperienceKind.PLAN, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        VectorType(1536), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("reference_id", "kind", name="uq_experience_reference_kind"),
    )


class ArtifactRecord(Base, TableNameMixin):
    """Metadata for artifacts stored in object storage."""

    task_id: Mapped[int] = mapped_column(ForeignKey("task_record.id"), nullable=False)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    task: Mapped[TaskRecord] = relationship()
