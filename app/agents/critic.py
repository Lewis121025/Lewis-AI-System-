"""Critic（点评）智能体：评估整体输出质量并给出反馈。"""

from __future__ import annotations

from app.agents.base import Agent, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest


class CriticAgent(Agent):
    """负责在流程末端进行质量把控，并可提示改进建议。"""

    def __init__(self, llm_proxy: LLMProxy) -> None:
        super().__init__("Critic")
        self.llm_proxy = llm_proxy

    def execute(self, context: AgentContext) -> AgentResponse:
        summary = context.payload.get("summary") or context.goal
        checklist = context.payload.get("checklist", [])

        prompt = (
            "You are the Critic agent. Evaluate the provided summary for completeness, "
            "correctness, and adherence to the checklist. Respond with JSON containing "
            "fields: verdict (approve/request_changes), score (0-1), issues (list of strings), "
            "and recommendations (list of strings).\n\n"
            f"Summary:\n{summary}\n\nChecklist:\n{checklist}"
        )
        response = self.llm_proxy.complete(
            LLMRequest(prompt=prompt, temperature=0.1, model=None)
        )

        # Since LLM response may not be JSON offline, create heuristic parsing.
        verdict = "approve" if "approve" in response.lower() else "request_changes"
        score = 0.8 if verdict == "approve" else 0.3
        issues = []
        if verdict != "approve":
            issues.append("LLM critique requested changes.")

        output = {
            "verdict": verdict,
            "score": score,
            "issues": issues,
            "raw_response": response,
        }
        return AgentResponse(success=True, output=output, message="Critique completed")
