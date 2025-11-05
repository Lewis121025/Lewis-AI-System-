"""FastAPI 路由定义：提供任务管理的 REST 与 WebSocket 接口。"""

from __future__ import annotations

import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.api.dependencies import get_orchestrator, require_token
from app.config import get_settings
from app.models.enums import TaskStatus
from app.orchestrator.orchestrator import TaskOrchestrator
from app.schemas.tasks import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskEvent,
    TaskStatusResponse,
)

router = APIRouter()


@router.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    """Health endpoint used for readiness checks."""
    return {"status": "ok"}


@router.post(
    "/tasks",
    response_model=TaskCreateResponse,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
async def create_task(
    payload: TaskCreateRequest,
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
) -> TaskCreateResponse:
    task_id = orchestrator.start_task(
        payload.goal,
        name=payload.name,
        metadata=payload.metadata,
        sync=payload.sync,
    )
    status = orchestrator.get_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found after creation")
    return TaskCreateResponse(task_id=task_id, status=TaskStatus(status["status"]))


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
async def get_task_status(
    task_id: str,
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
) -> TaskStatusResponse:
    status = orchestrator.get_status(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(
        task_id=status["task_id"],
        name=status["name"],
        goal=status["goal"],
        status=TaskStatus(status["status"]),
        started_at=status["started_at"],
        finished_at=status["finished_at"],
        result_summary=status.get("result_summary"),
        error_message=status.get("error_message"),
    )


@router.get(
    "/tasks/{task_id}/events",
    response_model=list[TaskEvent],
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
async def get_task_events(
    task_id: str,
    orchestrator: TaskOrchestrator = Depends(get_orchestrator),
) -> List[TaskEvent]:
    events = orchestrator.list_events(task_id)
    return [TaskEvent(**event) for event in events]


@router.websocket("/ws/tasks/{task_id}")
async def task_events_socket(websocket: WebSocket, task_id: str) -> None:
    """任务事件 WebSocket：用于从前端实时拉取事件日志。"""
    settings = get_settings()
    token = websocket.headers.get("authorization", "")
    if token != f"Bearer {settings.api_token}":
        await websocket.close(code=4401)
        return

    await websocket.accept()
    orchestrator = get_orchestrator()
    last_event_count = 0
    try:
        while True:
            events = orchestrator.list_events(task_id)
            if len(events) > last_event_count:
                new_events = events[last_event_count:]
                for event in new_events:
                    await websocket.send_json(event)
                last_event_count = len(events)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
