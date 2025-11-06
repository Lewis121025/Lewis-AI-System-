"""基于 LangGraph 的任务编排器：使用状态图管理智能体工作流。"""

from __future__ import annotations

import logging
import operator
import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, TypedDict, Annotated

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    # 兼容旧版本
    from langgraph.graph.state import StateGraph
    from langgraph.graph import END
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
from app.agents.researcher import ResearcherAgent
from app.agents.weather_agent import WeatherAgent
from app.infrastructure.cbr import CBRService
from app.infrastructure.db import get_session
from app.infrastructure.redis_queue import enqueue_job
from app.models.entities import TaskEventRecord, TaskRecord
from app.models.enums import ExperienceKind, TaskStatus

LOGGER = logging.getLogger(__name__)


class TaskState(TypedDict):
    """LangGraph 状态定义"""
    task_id: str
    goal: str
    name: str
    metadata: Dict[str, Any]
    status: str
    
    # Agent 输出
    perceptor_output: Optional[Dict[str, Any]]
    planner_output: Optional[Dict[str, Any]]
    execution_log: Annotated[List[Dict[str, Any]], operator.add]  # 累加列表
    prior_outputs: Dict[str, Any]
    
    # 最终结果
    result_summary: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    # 执行控制
    current_step_index: int
    plan: List[Dict[str, Any]]


class LangGraphOrchestrator:
    """基于 LangGraph 的任务编排器"""
    
    def __init__(
        self,
        *,
        perceptor: PerceptorAgent,
        planner: PlannerAgent,
        writer: WriterAgent,
        art_director: ArtDirectorAgent,
        toolsmith: ToolSmithAgent,
        researcher: ResearcherAgent,
        weather: WeatherAgent,
        critic: CriticAgent,
        cbr_service: CBRService,
        enable_queue: bool = True,
    ) -> None:
        self.perceptor = perceptor
        self.planner = planner
        self.writer = writer
        self.art_director = art_director
        self.researcher = researcher
        self.weather = weather
        self.toolsmith = toolsmith
        self.critic = critic
        self.cbr = cbr_service
        self.enable_queue = enable_queue
        self.logger = logging.getLogger("langgraph_orchestrator")
        
        self.agent_map: Dict[str, Agent] = {
            "Perceptor": self.perceptor,
            "Planner": self.planner,
            "Writer": self.writer,
            "ArtDirector": self.art_director,
            "ToolSmith": self.toolsmith,
            "Researcher": self.researcher,
            "Weather": self.weather,
            "Critic": self.critic,
        }
        
        # 构建 LangGraph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        workflow = StateGraph(TaskState)
        
        # 添加节点
        workflow.add_node("perceptor", self._perceptor_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("execute_plan", self._execute_plan_node)
        workflow.add_node("critic", self._critic_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # 定义边
        workflow.set_entry_point("perceptor")
        workflow.add_edge("perceptor", "planner")
        workflow.add_edge("planner", "execute_plan")
        workflow.add_conditional_edges(
            "execute_plan",
            self._should_continue_execution,
            {
                "continue": "execute_plan",
                "critic": "critic",
            }
        )
        workflow.add_edge("critic", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow
    
    def _perceptor_node(self, state: TaskState) -> TaskState:
        """Perceptor 节点：感知任务并分解"""
        task_id = state["task_id"]
        goal = state["goal"]
        metadata = state.get("metadata", {})
        
        try:
            ctx = AgentContext(task_id=task_id, goal=goal, payload=metadata)
            result = self.perceptor.execute(ctx)
            
            if not result.success:
                raise RuntimeError("Perceptor failed to derive tasks.")
            
            self._record_event(task_id, "perception_completed", _response_to_dict(result))
            
            state["perceptor_output"] = result.output
            return state
        except Exception as exc:
            self.logger.exception("Perceptor failed: %s", exc)
            state["error_message"] = str(exc)
            state["status"] = TaskStatus.FAILED.value
            return state
    
    def _planner_node(self, state: TaskState) -> TaskState:
        """Planner 节点：生成执行计划"""
        task_id = state["task_id"]
        goal = state["goal"]
        perceptor_output = state.get("perceptor_output", {})
        tasks = perceptor_output.get("tasks", [])
        
        try:
            ctx = AgentContext(
                task_id=task_id,
                goal=goal,
                payload={"tasks": tasks},
                prior_outputs={"perceptor": perceptor_output},
            )
            result = self.planner.execute(ctx)
            plan = result.output.get("plan", [])
            
            self._record_event(task_id, "planning_completed", _response_to_dict(result))
            
            state["planner_output"] = result.output
            state["plan"] = plan
            state["current_step_index"] = 0
            state["prior_outputs"] = {
                "perceptor": perceptor_output,
                "planner": result.output,
            }
            state["execution_log"] = []
            
            return state
        except Exception as exc:
            self.logger.exception("Planner failed: %s", exc)
            state["error_message"] = str(exc)
            state["status"] = TaskStatus.FAILED.value
            return state
    
    def _execute_plan_node(self, state: TaskState) -> TaskState:
        """执行计划节点：执行单个步骤"""
        task_id = state["task_id"]
        goal = state["goal"]
        plan = state.get("plan", [])
        step_index = state.get("current_step_index", 0)
        prior_outputs = state.get("prior_outputs", {})
        execution_log = state.get("execution_log", [])
        metadata = state.get("metadata", {})
        
        if step_index >= len(plan):
            # 所有步骤执行完毕
            return state
        
        step = plan[step_index]
        agent_name = step.get("agent", "Writer")
        agent = self.agent_map.get(agent_name)
        
        if agent is None:
            self.logger.warning("No agent mapped for %s, skipping", agent_name)
            state["current_step_index"] = step_index + 1
            return state
        
        try:
            payload = {
                "task": step.get("description", ""),
                "step_index": step_index + 1,
                "metadata": metadata,
                "requires_review": step.get("requires_review", False),
            }
            ctx = AgentContext(
                task_id=task_id,
                goal=goal,
                payload=payload,
                prior_outputs=prior_outputs,
            )
            
            response = agent.execute(ctx)
            
            # 更新状态
            prior_outputs[agent_name.lower()] = response.output
            log_entry = {
                "step": step,
                "agent": agent_name,
                "response": _response_to_dict(response),
            }
            
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
                error_msg = response.message or "Unknown error"
                error_detail = f"Step {step_index + 1} handled by {agent_name} failed: {error_msg}"
                self.logger.error(error_detail)
                raise RuntimeError(error_detail)
            
            state["prior_outputs"] = prior_outputs
            state["execution_log"] = [log_entry]  # LangGraph 会自动累加
            state["current_step_index"] = step_index + 1
            
            return state
            
        except Exception as exc:
            self.logger.exception("Agent %s failed at step %d: %s", agent_name, step_index + 1, exc)
            state["error_message"] = str(exc)
            state["status"] = TaskStatus.FAILED.value
            return state
    
    def _should_continue_execution(self, state: TaskState) -> str:
        """判断是否继续执行计划"""
        plan = state.get("plan", [])
        step_index = state.get("current_step_index", 0)
        
        if step_index >= len(plan):
            return "critic"
        return "continue"
    
    def _critic_node(self, state: TaskState) -> TaskState:
        """Critic 节点：最终评审"""
        task_id = state["task_id"]
        goal = state["goal"]
        plan = state.get("plan", [])
        execution_log = state.get("execution_log", [])
        prior_outputs = state.get("prior_outputs", {})
        
        try:
            ctx = AgentContext(
                task_id=task_id,
                goal=goal,
                payload={
                    "summary": {
                        "goal": goal,
                        "plan": plan,
                        "execution_log": execution_log,
                    },
                    "checklist": [],
                },
                prior_outputs=prior_outputs,
            )
            result = self.critic.execute(ctx)
            
            log_entry = {
                "step": {"description": "Final critique", "agent": "Critic"},
                "agent": "Critic",
                "response": _response_to_dict(result),
            }
            
            self._record_event(task_id, "critic_completed", _response_to_dict(result))
            
            # 获取现有的 execution_log 并添加新条目
            existing_log = state.get("execution_log", [])
            # 由于使用了 Annotated[List, operator.add]，返回新条目列表即可
            state["execution_log"] = [log_entry]
            # 构建完整的 execution_log 用于 result_summary
            full_execution_log = existing_log + [log_entry]
            state["result_summary"] = {
                "goal": goal,
                "plan": plan,
                "execution": full_execution_log,
                "verdict": result.output,
            }
            
            return state
        except Exception as exc:
            self.logger.exception("Critic failed: %s", exc)
            state["error_message"] = str(exc)
            state["status"] = TaskStatus.FAILED.value
            return state
    
    def _finalize_node(self, state: TaskState) -> TaskState:
        """最终化节点：保存结果和经验"""
        task_id = state["task_id"]
        goal = state["goal"]
        name = state.get("name", goal[:120])
        plan = state.get("plan", [])
        # execution_log 可能是一个列表的列表（由于 Annotated[List, operator.add]）
        # 需要展平
        execution_log_raw = state.get("execution_log", [])
        if execution_log_raw and isinstance(execution_log_raw[0], list):
            # 展平嵌套列表
            execution_log = [item for sublist in execution_log_raw for item in sublist]
        else:
            execution_log = execution_log_raw if isinstance(execution_log_raw, list) else []
        result_summary = state.get("result_summary")
        error_message = state.get("error_message")
        
        try:
            if error_message:
                self._update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error_message=error_message,
                    finished_at=datetime.now(UTC),
                )
                self._record_event(task_id, "task_failed", {"error": error_message})
            else:
                self._update_task_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result_summary=result_summary,
                    finished_at=datetime.now(UTC),
                )
                
                # 保存经验
                plan_description = "\n".join(step.get("description", "") for step in plan)
                self.cbr.add_experience(
                    reference_id=task_id,
                    kind=ExperienceKind.PLAN,
                    title=name,
                    content=f"Goal: {goal}\nPlan:\n{plan_description}",
                    metadata={"execution_log": execution_log},
                )
            
            state["status"] = TaskStatus.COMPLETED.value if not error_message else TaskStatus.FAILED.value
            return state
        except Exception as exc:
            self.logger.exception("Finalize failed: %s", exc)
            state["error_message"] = str(exc)
            state["status"] = TaskStatus.FAILED.value
            return state
    
    # --------------------------------------------------------------------- Public API
    
    def start_task(
        self,
        goal: str,
        *,
        name: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        sync: bool = False,
    ) -> str:
        """创建任务并触发执行"""
        metadata = metadata or {}
        task_id = uuid.uuid4().hex
        name = name or goal[:120]
        self._create_task_record(task_id, name, goal, metadata)
        self._record_event(task_id, "created", {"metadata": metadata})
        
        if not sync and self.enable_queue:
            try:
                enqueue_job(process_task_job, task_id)
                self._record_event(task_id, "queued", {})
                self.logger.info("Task %s enqueued successfully. Make sure RQ worker is running.", task_id)
                return task_id
            except Exception as exc:
                self.logger.warning("Failed to enqueue task %s: %s. Falling back to synchronous execution.", task_id, exc)
                # 如果队列不可用，回退到同步执行
                self._record_event(task_id, "queue_failed", {"error": str(exc), "fallback": "synchronous"})
        
        # 同步执行（包括回退情况）
        self.logger.info("Executing task %s synchronously", task_id)
        self.execute_task(task_id)
        return task_id
    
    def execute_task(self, task_id: str) -> None:
        """执行任务（使用 LangGraph）"""
        record = self._get_task_record(task_id)
        if record is None:
            raise RuntimeError(f"Task {task_id} not found.")
        
        goal = record.goal
        metadata = record.meta or {}
        name = record.name
        
        self._update_task_status(task_id, TaskStatus.RUNNING, started_at=datetime.now(UTC))
        
        # 初始化状态
        initial_state: TaskState = {
            "task_id": task_id,
            "goal": goal,
            "name": name,
            "metadata": metadata,
            "status": TaskStatus.RUNNING.value,
            "perceptor_output": None,
            "planner_output": None,
            "execution_log": [],
            "prior_outputs": {},
            "result_summary": None,
            "error_message": None,
            "current_step_index": 0,
            "plan": [],
        }
        
        try:
            # 运行 LangGraph，增加递归限制以支持复杂任务
            final_state = self.app.invoke(
                initial_state,
                config={"recursion_limit": 100}
            )
            
            # 状态已在 finalize_node 中更新，这里不需要额外操作
            if final_state.get("error_message"):
                raise RuntimeError(final_state["error_message"])
                
        except Exception as exc:
            LOGGER.exception("Task %s failed: %s", task_id, exc)
            self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=str(exc),
                finished_at=datetime.now(UTC),
            )
            self._record_event(task_id, "task_failed", {"error": str(exc)})
            raise
    
    def get_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """返回任务状态和摘要"""
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
        """检索任务的事件日志"""
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
    """后台工作入口点（用于 RQ）"""
    from app.orchestrator.factory import build_orchestrator
    
    orchestrator = build_orchestrator()
    orchestrator.execute_task(task_id)

