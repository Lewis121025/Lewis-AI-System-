"""Planner（规划）智能体：负责根据经验库生成执行计划。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.infrastructure.cbr import CBRService, RetrievedCase
from app.models.enums import ExperienceKind


@dataclass
class PlanStep:
    """单个计划步骤的结构表示。"""

    description: str
    agent: str
    requires_review: bool = False

    def to_dict(self) -> dict[str, str]:
        payload = {
            "description": self.description,
            "agent": self.agent,
        }
        if self.requires_review:
            payload["requires_review"] = True
        return payload


class PlannerAgent(Agent):
    """综合历史案例与当前任务，输出可执行的步骤序列。"""

    def __init__(self, llm_proxy: LLMProxy, cbr_service: CBRService) -> None:
        super().__init__("Planner")
        self.llm_proxy = llm_proxy
        self.cbr = cbr_service

    def execute(self, context: AgentContext) -> AgentResponse:
        goal = context.goal
        initial_tasks = context.payload.get("tasks", [])
        references = self.cbr.find_similar(goal, kind=ExperienceKind.PLAN, limit=3)
        plan = self._build_plan(goal, initial_tasks, references)

        serialized = [step.to_dict() for step in plan]
        metadata = {
            "references": [case.reference_id for case in references],
            "step_count": len(plan),
        }
        return AgentResponse(
            success=True,
            output={"plan": serialized, "metadata": metadata},
            message="Planning completed",
        )

    def _build_plan(
        self, goal: str, tasks: List[str], references: List[RetrievedCase]
    ) -> List[PlanStep]:
        if not tasks:
            tasks = self._llm_breakdown(goal)
        
        plan: List[PlanStep] = []
        seen_visual_cue = False
        has_search_task = False
        
        for task in tasks:
            agent_name = self._assign_agent(task)
            requires_review = agent_name in {"Writer", "ToolSmith"}
            
            if agent_name == "ArtDirector":
                seen_visual_cue = True
            if agent_name == "Researcher":
                has_search_task = True
            
            plan.append(
                PlanStep(description=task, agent=agent_name, requires_review=requires_review)
            )

        # 对于搜索任务，确保不添加冗余步骤
        if seen_visual_cue:
            plan.append(
                PlanStep(description="Review visual assets", agent="Critic", requires_review=True)
            )

        # 只在非搜索任务时应用历史经验
        if not has_search_task:
            for case in references:
                note = (case.metadata or {}).get("insight")
                if note:
                    plan.append(
                        PlanStep(description=f"Apply lesson: {note}", agent="Writer")
                    )
        
        # 最终评审
        plan.append(
            PlanStep(description="Final quality review", agent="Critic", requires_review=True)
        )
        return plan

    def _llm_breakdown(self, goal: str) -> List[str]:
        # 检测简单任务，不需要复杂分解
        goal_lower = goal.lower()
        simple_keywords = [
            "hello world", "hello, world", "打印", "输出", 
            "简单", "basic", "simple"
        ]
        
        # 检测搜索任务，不要分解
        search_keywords = [
            "search", "google", "find", "look up", "query",
            "搜索", "查询", "查找", "检索"
        ]
        
        # 如果是简单任务或搜索任务，不要过度分解
        if (any(keyword in goal_lower for keyword in simple_keywords) or 
            any(keyword in goal_lower for keyword in search_keywords)):
            # 对于简单任务和搜索任务，只返回任务本身
            return [goal]
        
        # 对于复杂任务，使用 LLM 分解
        prompt = (
            "Decompose the following goal into 2-4 concrete steps. "
            "For simple tasks like 'write a hello world program', return just 1 step. "
            "For complex tasks, break them down logically. "
            "Return each step on a new line without numbering and using imperative verbs.\n"
            f"Goal: {goal}"
        )
        response = self.llm_proxy.complete(LLMRequest(prompt=prompt, temperature=0.4))
        steps = [line.strip("-• ").strip() for line in response.splitlines() if line.strip()]
        return steps[:5] or [goal]

    @staticmethod
    def _assign_agent(task_description: str) -> str:
        lowered = task_description.lower()
        
        # 优先级1: 天气任务 -> Weather Agent
        weather_keywords = ("weather", "天气", "气温", "forecast", "预报")
        if any(keyword in lowered for keyword in weather_keywords):
            return "Weather"
        
        # 优先级2: 视觉任务
        if any(keyword in lowered for keyword in ("diagram", "image", "visual", "plot")):
            return "ArtDirector"
        
        # 优先级3: 评审任务
        if any(keyword in lowered for keyword in ("test", "review", "validate")):
            return "Critic"
        
        # 优先级4: 工具任务
        if any(keyword in lowered for keyword in ("tool", "utility", "helper")):
            return "ToolSmith"
        
        # 优先级5: 搜索任务
        search_keywords = (
            "search", "find", "look up", "research", "query", "google",
            "搜索", "查找", "研究", "查询", "检索"
        )
        if any(keyword in lowered for keyword in search_keywords):
            return "Researcher"
        
        # 默认: 代码生成
        return "Writer"
