"""SQLAlchemy 基类与通用 Mixin 定义。"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型共享的基类，包含通用字段。"""

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
    """自动根据类名生成蛇形表名的 Mixin。"""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[misc]
        """根据类名生成 snake_case 表名。"""
        name = []
        for idx, char in enumerate(cls.__name__):
            if char.isupper() and idx > 0:
                name.append("_")
            name.append(char.lower())
        return "".join(name)


class JSONMixin:
    """为存储 JSON 的模型提供序列化辅助方法。"""

    def to_dict(self) -> dict[str, Any]:
        """将模型字段序列化为字典，便于日志或 API 返回。"""
        return {
            column.key: getattr(self, column.key)
            for column in self.__table__.columns  # type: ignore[attr-defined]
        }
