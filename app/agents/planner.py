"""Planner agent responsible for sequencing tasks and leveraging CBR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.infrastructure.cbr import CBRService, RetrievedCase
from app.models.enums import ExperienceKind


@dataclass
class PlanStep:
    """Structured representation of a single plan step."""

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
    """Generate a plan informed by past experiences."""

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
        for task in tasks:
            agent_name = self._assign_agent(task)
            requires_review = agent_name in {"Writer", "ToolSmith"}
            if agent_name == "ArtDirector":
                seen_visual_cue = True
            plan.append(
                PlanStep(description=task, agent=agent_name, requires_review=requires_review)
            )

        if seen_visual_cue:
            plan.append(
                PlanStep(description="Review visual assets", agent="Critic", requires_review=True)
            )

        # Leverage references to append insights.
        for case in references:
            if note := case.metadata.get("insight"):
                plan.append(
                    PlanStep(description=f"Apply lesson: {note}", agent="Writer")
                )
        plan.append(
            PlanStep(description="Final quality review and summary", agent="Critic", requires_review=True)
        )
        return plan

    def _llm_breakdown(self, goal: str) -> List[str]:
        prompt = (
            "Decompose the following goal into 4 concrete steps. "
            "Return each step on a new line without numbering and using imperative verbs.\n"
            f"Goal: {goal}"
        )
        response = self.llm_proxy.complete(LLMRequest(prompt=prompt, temperature=0.4))
        steps = [line.strip("-• ").strip() for line in response.splitlines() if line.strip()]
        return steps[:5] or [goal]

    @staticmethod
    def _assign_agent(task_description: str) -> str:
        lowered = task_description.lower()
        if any(keyword in lowered for keyword in ("diagram", "image", "visual", "plot")):
            return "ArtDirector"
        if any(keyword in lowered for keyword in ("test", "review", "validate")):
            return "Critic"
        if any(keyword in lowered for keyword in ("tool", "utility", "helper")):
            return "ToolSmith"
        return "Writer"
