"""任务编排器：贯穿三层架构，协调整个智能体工作流。"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select

from app.agents import (
    Agent,
    AgentContext,
    AgentResponse,
    ArtDirectorAgent,
    CriticAgent,
    PerceptorAgent,
    PlannerAgent,
    ToolSmithAgent,
    WriterAgent,
)
from app.infrastructure.cbr import CBRService
from app.infrastructure.db import get_session
from app.infrastructure.redis_queue import enqueue_job
from app.models.entities import TaskEventRecord, TaskRecord
from app.models.enums import ExperienceKind, TaskStatus

LOGGER = logging.getLogger(__name__)


class TaskOrchestrator:
    """协调感知、规划、执行等智能体的任务编排核心。"""

    def __init__(
        self,
        *,
        perceptor: PerceptorAgent,
        planner: PlannerAgent,
        writer: WriterAgent,
        art_director: ArtDirectorAgent,
        toolsmith: ToolSmithAgent,
        critic: CriticAgent,
        cbr_service: CBRService,
        enable_queue: bool = True,
    ) -> None:
        self.perceptor = perceptor
        self.planner = planner
        self.writer = writer
        self.art_director = art_director
        self.toolsmith = toolsmith
        self.critic = critic
        self.cbr = cbr_service
        self.enable_queue = enable_queue
        self.logger = logging.getLogger("orchestrator")

        self.agent_map: Dict[str, Agent] = {
            "Perceptor": self.perceptor,
            "Planner": self.planner,
            "Writer": self.writer,
            "ArtDirector": self.art_director,
            "ToolSmith": self.toolsmith,
            "Critic": self.critic,
        }

    # --------------------------------------------------------------------- Public API

    def start_task(
        self,
        goal: str,
        *,
        name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        sync: bool = False,
    ) -> str:
        """Create a task record and trigger execution."""
        metadata = metadata or {}
        task_id = uuid.uuid4().hex
        name = name or goal[:120]
        self._create_task_record(task_id, name, goal, metadata)
        self._record_event(task_id, "created", {"metadata": metadata})

        if not sync and self.enable_queue:
            try:
                enqueue_job(process_task_job, task_id)
                self._record_event(task_id, "queued", {})
                return task_id
            except Exception as exc:  # pragma: no cover - redis unavailable
                self.logger.warning("Falling back to synchronous execution: %s", exc)

        self.execute_task(task_id)
        return task_id

    def execute_task(self, task_id: str) -> None:
        """Execute the task pipeline synchronously."""
        record = self._get_task_record(task_id)
        if record is None:
            raise RuntimeError(f"Task {task_id} not found.")

        goal = record.goal
        metadata = record.meta or {}
        self._update_task_status(task_id, TaskStatus.RUNNING, started_at=datetime.utcnow())

        try:
            # L3 perception
            perceptor_ctx = AgentContext(task_id=task_id, goal=goal, payload=metadata)
            perceptor_result = self.perceptor.execute(perceptor_ctx)
            if not perceptor_result.success:
                raise RuntimeError("Perceptor failed to derive tasks.")
            self._record_event(task_id, "perception_completed", _response_to_dict(perceptor_result))

            tasks = perceptor_result.output.get("tasks", [])
            planner_ctx = AgentContext(
                task_id=task_id,
                goal=goal,
                payload={"tasks": tasks},
                prior_outputs={"perceptor": perceptor_result.output},
            )
            planner_result = self.planner.execute(planner_ctx)
            plan = planner_result.output.get("plan", [])
            self._record_event(task_id, "planning_completed", _response_to_dict(planner_result))

            prior_outputs: dict[str, Any] = {
                "perceptor": perceptor_result.output,
                "planner": planner_result.output,
            }
            execution_log: List[dict[str, Any]] = []

            for index, step in enumerate(plan, start=1):
                agent_name = step.get("agent", "Writer")
                agent = self.agent_map.get(agent_name)
                if agent is None:
                    self.logger.warning("No agent mapped for %s, skipping", agent_name)
                    continue

                payload = {
                    "task": step.get("description", ""),
                    "step_index": index,
                    "metadata": metadata,
                    "requires_review": step.get("requires_review", False),
                }
                context = AgentContext(
                    task_id=task_id,
                    goal=goal,
                    payload=payload,
                    prior_outputs=prior_outputs,
                )
                try:
                    response = agent.execute(context)
                except Exception as exc:  # pragma: no cover - defensive
                    self._record_event(
                        task_id,
                        f"{agent_name.lower()}_error",
                        {"error": str(exc), "step": step},
                    )
                    raise

                prior_outputs[agent_name.lower()] = response.output
                execution_log.append(
                    {
                        "step": step,
                        "agent": agent_name,
                        "response": _response_to_dict(response),
                    }
                )
                status = "completed" if response.success else "failed"
                self._record_event(
                    task_id,
                    f"{agent_name.lower()}_{status}",
                    {
                        "step": step,
                        "response": _response_to_dict(response),
                    },
                )
                if not response.success:
                    raise RuntimeError(f"Step {index} handled by {agent_name} failed.")

            # Final critic evaluation
            critic_ctx = AgentContext(
                task_id=task_id,
                goal=goal,
                payload={
                    "summary": {
                        "goal": goal,
                        "plan": plan,
                        "execution_log": execution_log,
                    }
                },
                prior_outputs=prior_outputs,
            )
            critic_result = self.critic.execute(critic_ctx)
            execution_log.append(
                {
                    "step": {"description": "Final critique", "agent": "Critic"},
                    "agent": "Critic",
                    "response": _response_to_dict(critic_result),
                }
            )
            self._record_event(
                task_id,
                "critic_completed",
                _response_to_dict(critic_result),
            )

            final_summary = {
                "goal": goal,
                "plan": plan,
                "execution": execution_log,
                "verdict": critic_result.output,
            }
            self._update_task_status(
                task_id,
                TaskStatus.COMPLETED,
                result_summary=final_summary,
                finished_at=datetime.utcnow(),
                error_message=None,
            )

            # Persist experience
            plan_description = "\n".join(step.get("description", "") for step in plan)
            self.cbr.add_experience(
                reference_id=task_id,
                kind=ExperienceKind.PLAN,
                title=record.name,
                content=f"Goal: {goal}\nPlan:\n{plan_description}",
                metadata={"execution_log": execution_log},
            )

        except Exception as exc:
            LOGGER.exception("Task %s failed: %s", task_id, exc)
            self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=str(exc),
                finished_at=datetime.utcnow(),
            )
            self._record_event(task_id, "task_failed", {"error": str(exc)})
            raise

    def get_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """Return task status and summary."""
        record = self._get_task_record(task_id)
        if record is None:
            return None
        return {
            "task_id": task_id,
            "name": record.name,
            "goal": record.goal,
            "status": record.status.value,
            "result_summary": record.result_summary,
            "error_message": record.error_message,
            "started_at": record.started_at,
            "finished_at": record.finished_at,
        }

    def list_events(self, task_id: str) -> list[dict[str, Any]]:
        """Retrieve chronological event logs for a task."""
        with get_session() as session:
            record = session.scalar(select(TaskRecord).where(TaskRecord.task_id == task_id))
            if record is None:
                return []
            events = (
                session.query(TaskEventRecord)
                .filter(TaskEventRecord.task_id == record.id)
                .order_by(TaskEventRecord.created_at)
                .all()
            )
            return [
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "created_at": event.created_at,
                }
                for event in events
            ]

    # --------------------------------------------------------------------- Internals

    def _create_task_record(
        self, task_id: str, name: str, goal: str, metadata: dict[str, Any]
    ) -> None:
        with get_session() as session:
            record = TaskRecord(
                task_id=task_id,
                name=name,
                goal=goal,
                meta=metadata,
                status=TaskStatus.PENDING,
            )
            session.add(record)

    def _get_task_record(self, task_id: str) -> Optional[TaskRecord]:
        with get_session() as session:
            return session.scalar(select(TaskRecord).where(TaskRecord.task_id == task_id))

    def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        *,
        result_summary: Optional[dict[str, Any]] = None,
        error_message: Optional[str] = None,
        started_at: Optional[datetime] = None,
        finished_at: Optional[datetime] = None,
    ) -> None:
        with get_session() as session:
            record = session.scalar(select(TaskRecord).where(TaskRecord.task_id == task_id))
            if record is None:
                return
            record.status = status
            if result_summary is not None:
                record.result_summary = result_summary
            if error_message is not None:
                record.error_message = error_message
            if started_at is not None:
                record.started_at = started_at
            if finished_at is not None:
                record.finished_at = finished_at

    def _record_event(self, task_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with get_session() as session:
            record = session.scalar(select(TaskRecord).where(TaskRecord.task_id == task_id))
            if record is None:
                return
            event = TaskEventRecord(
                task_id=record.id,
                event_type=event_type,
                payload=payload,
            )
            session.add(event)


def _response_to_dict(response: AgentResponse) -> dict[str, Any]:
    return {
        "success": response.success,
        "output": response.output,
        "message": response.message,
        "artifacts": [
            {"uri": artifact.uri, "description": artifact.description, "media_type": artifact.media_type}
            for artifact in response.artifacts
        ],
    }


def process_task_job(task_id: str) -> None:
    """Background worker entry point used by RQ."""
    from app.orchestrator.factory import build_orchestrator

    orchestrator = build_orchestrator()
    orchestrator.execute_task(task_id)
