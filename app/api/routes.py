"""FastAPI 路由定义：提供任务管理的 REST 与 WebSocket 接口。"""

from __future__ import annotations

import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from app.api.dependencies import get_orchestrator, require_token
from app.config import get_settings
from app.models.enums import TaskStatus
from app.orchestrator.langgraph_orchestrator import LangGraphOrchestrator
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


@router.get("/queue/status", tags=["system"], dependencies=[Depends(require_token)])
async def get_queue_status() -> dict[str, Any]:
    """检查队列和 Worker 状态。"""
    from app.infrastructure.redis_queue import get_redis_connection, get_queue
    from rq import Worker
    
    status = {
        "redis_available": False,
        "queue_available": False,
        "workers_running": 0,
        "queue_length": 0,
        "message": ""
    }
    
    try:
        # 检查 Redis 连接
        conn = get_redis_connection()
        conn.ping()
        status["redis_available"] = True
        
        # 检查队列
        queue = get_queue()
        status["queue_available"] = True
        status["queue_length"] = len(queue)
        
        # 检查 Worker
        workers = Worker.all(connection=conn)
        status["workers_running"] = len(workers)
        
        if status["workers_running"] == 0:
            status["message"] = "⚠️ Redis 队列可用，但没有 Worker 在运行。请启动 Worker 以处理异步任务。"
        else:
            status["message"] = f"✅ 队列正常，{status['workers_running']} 个 Worker 正在运行。"
            
    except Exception as exc:
        status["message"] = f"❌ Redis 不可用: {str(exc)}。异步任务将回退到同步执行。"
    
    return status


@router.post(
    "/tasks",
    response_model=TaskCreateResponse,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
async def create_task(
    payload: TaskCreateRequest,
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
) -> TaskCreateResponse:
    """创建任务端点。同步模式会在后台线程执行，避免阻塞事件循环。"""
    try:
        # 如果使用同步模式，在线程池中执行以避免阻塞事件循环
        if payload.sync:
            # 使用 asyncio.to_thread 在线程池中执行同步任务
            # 这样可以避免阻塞 FastAPI 的事件循环
            task_id = await asyncio.to_thread(
                orchestrator.start_task,
                payload.goal,
                name=payload.name,
                metadata=payload.metadata,
                sync=True,
            )
        else:
            # 异步模式直接调用，会快速返回任务ID
            task_id = orchestrator.start_task(
                payload.goal,
                name=payload.name,
                metadata=payload.metadata,
                sync=False,
            )
        
        status = orchestrator.get_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found after creation")
        return TaskCreateResponse(task_id=task_id, status=TaskStatus(status["status"]))
    except Exception as exc:
        # 记录详细错误信息以便调试
        import logging
        logger = logging.getLogger("api")
        logger.exception("Failed to create task: %s", exc)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(exc)}")


@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    dependencies=[Depends(require_token)],
    tags=["tasks"],
)
async def get_task_status(
    task_id: str,
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
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
    orchestrator: LangGraphOrchestrator = Depends(get_orchestrator),
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
