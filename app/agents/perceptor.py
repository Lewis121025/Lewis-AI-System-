"""Perceptor agent responsible for initial task derivation."""

from __future__ import annotations

from typing import List

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest


class PerceptorAgent(Agent):
    """Derive actionable tasks from a high-level problem statement."""

    def __init__(self, llm_proxy: LLMProxy) -> None:
        super().__init__("Perceptor")
        self.llm_proxy = llm_proxy

    def execute(self, context: AgentContext) -> AgentResponse:
        goal = context.goal or context.payload.get("prompt", "")
        tasks = self._derive_tasks(goal)
        return AgentResponse(
            success=True,
            output={"tasks": tasks, "task_count": len(tasks)},
            message="Perception completed",
        )

    def _derive_tasks(self, goal: str) -> List[str]:
        if not goal:
            return ["Clarify the user's goal."]

        # Basic heuristic: split bullet points or sentences from input.
        tokens = [token.strip("-• ").strip() for token in goal.splitlines() if token.strip()]
        if len(tokens) > 1:
            return tokens

        prompt = (
            "You are the Perceptor agent. Given the following goal, produce a concise "
            "ordered list of 3-5 high-level tasks. Use short imperative phrases.\n\n"
            f"Goal:\n{goal}"
        )
        response_text = self.llm_proxy.complete(
            LLMRequest(prompt=prompt, provider=None, model=None, temperature=0.3)
        )

        lines = [line.strip("-• ").strip() for line in response_text.splitlines()]
        cleaned = [line for line in lines if line]
        if not cleaned:
            cleaned = [goal]
        return cleaned[:5]
