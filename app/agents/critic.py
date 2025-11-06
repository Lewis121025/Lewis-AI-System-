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
        summary_data = context.payload.get("summary")
        checklist = context.payload.get("checklist", [])
        
        # 如果summary是字典结构，提取关键信息
        if isinstance(summary_data, dict):
            goal = summary_data.get("goal", "")
            execution_log = summary_data.get("execution_log", [])
            
            # 提取最后一步的实际输出
            final_output = None
            final_code = None
            final_stdout = None
            
            for entry in reversed(execution_log):
                if entry.get("agent") == "Writer":
                    response_output = entry.get("response", {}).get("output", {})
                    if response_output:
                        final_code = response_output.get("code")
                        sandbox = response_output.get("sandbox", {})
                        if sandbox and sandbox.get("success"):
                            final_stdout = sandbox.get("stdout")
                            break
            
            # 构建清晰的摘要文本
            summary_text = f"Task Goal: {goal}\n\n"
            if final_code:
                summary_text += f"Final Generated Code:\n```python\n{final_code}\n```\n\n"
            if final_stdout:
                summary_text += f"Execution Output:\n{final_stdout}\n\n"
            summary_text += f"Total steps executed: {len(execution_log)}"
        else:
            summary_text = str(summary_data)

        # 检查是否为搜索任务
        is_search_task = "search" in summary_text.lower() or "搜索" in summary_text or "查询" in summary_text
        
        if is_search_task:
            prompt = (
                "You are the Critic agent. Review this search task execution.\n\n"
                "For search tasks, verify:\n"
                "1. Was a real search performed (not mock data)?\n"
                "2. Are the search results relevant to the query?\n"
                "3. If there's code generation after search, does it use the search results?\n"
                "4. Is the output meaningful and correct?\n\n"
                "Respond with JSON:\n"
                "- verdict: 'approve' if search was performed and used correctly, 'request_changes' if not\n"
                "- score: 0.8-1.0 for good results, 0.5-0.8 for partial completion, 0.0-0.5 for major issues\n"
                "- issues: list problems (empty if none)\n"
                "- recommendations: list suggestions (empty if none)\n\n"
                f"Results:\n{summary_text}\n\n"
                f"Checklist: {checklist if checklist else 'N/A'}"
            )
        else:
            prompt = (
                "You are the Critic agent. Review the task execution results below.\n"
                "Your job is to verify:\n"
                "1. The code successfully accomplishes the stated goal\n"
                "2. The execution output is correct\n"
                "3. There are no obvious errors or issues\n\n"
                "Respond with JSON containing:\n"
                "- verdict: 'approve' if the task is completed successfully, 'request_changes' if not\n"
                "- score: 0.0-1.0 (1.0 = perfect)\n"
                "- issues: list of any problems found (empty if none)\n"
                "- recommendations: list of suggestions (empty if none)\n\n"
                f"Task Execution Results:\n{summary_text}\n\n"
                f"Checklist: {checklist if checklist else 'No specific checklist provided'}"
            )
        response = self.llm_proxy.complete(
            LLMRequest(prompt=prompt, temperature=0.1, model=None)
        )

        # Parse JSON response with better error handling
        import json
        import re
        
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                verdict = parsed.get("verdict", "approve")
                score = float(parsed.get("score", 0.9))
                issues = parsed.get("issues", [])
                recommendations = parsed.get("recommendations", [])
            except (json.JSONDecodeError, ValueError):
                verdict = "approve" if "approve" in response.lower() else "request_changes"
                score = 0.9 if verdict == "approve" else 0.3
                issues = [] if verdict == "approve" else ["Failed to parse critic response"]
                recommendations = []
        else:
            # Fallback to heuristic parsing
            verdict = "approve" if "approve" in response.lower() else "request_changes"
            score = 0.9 if verdict == "approve" else 0.3
            issues = [] if verdict == "approve" else ["LLM critique requested changes."]
            recommendations = []

        output = {
            "verdict": verdict,
            "score": score,
            "issues": issues,
            "recommendations": recommendations if recommendations else [],
            "raw_response": response,
        }
        return AgentResponse(success=True, output=output, message="Critique completed")
