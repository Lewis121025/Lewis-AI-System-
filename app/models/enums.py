"""枚举类型：统一表示任务状态、经验案例类型等。"""

from enum import Enum


class TaskStatus(str, Enum):
    """High-level lifecycle states for orchestrated tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExperienceKind(str, Enum):
    """Types of cases stored in the CBR repository."""

    PLAN = "plan"
    TOOL = "tool"
    ARTIFACT = "artifact"
