"""SQLAlchemy declarative base and shared mixins."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base registry for all SQLAlchemy models."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TableNameMixin:
    """Automatically derive table names from class names."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[misc]
        """Return snake_case table names."""
        name = []
        for idx, char in enumerate(cls.__name__):
            if char.isupper() and idx > 0:
                name.append("_")
            name.append(char.lower())
        return "".join(name)


class JSONMixin:
    """Utility mixin for models storing JSON payloads."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize model fields into a dictionary."""
        return {
            column.key: getattr(self, column.key)
            for column in self.__table__.columns  # type: ignore[attr-defined]
        }
