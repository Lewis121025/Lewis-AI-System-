"""Enumerations used across persistence models."""

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
