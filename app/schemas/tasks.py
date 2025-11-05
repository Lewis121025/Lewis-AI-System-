"""Pydantic schemas for task API."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import TaskStatus


class TaskCreateRequest(BaseModel):
    goal: str = Field(..., description="High-level goal for the orchestrator")
    name: Optional[str] = Field(None, description="Optional friendly task name")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sync: bool = Field(False, description="Execute synchronously when true")


class TaskCreateResponse(BaseModel):
    task_id: str
    status: TaskStatus


class TaskStatusResponse(BaseModel):
    task_id: str
    name: str
    goal: str
    status: TaskStatus
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    result_summary: Optional[Dict[str, Any]]
    error_message: Optional[str]


class TaskEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    created_at: datetime


class TaskListResponse(BaseModel):
    items: List[TaskStatusResponse]
