"""ToolSmith agent creates utilities on demand."""

from __future__ import annotations

from typing import Optional

from app.agents.base import Agent, AgentArtifact, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.agents.sandbox import Sandbox
from app.infrastructure.storage import ObjectStorageClient


class ToolSmithAgent(Agent):
    """Generate and validate helper tools in the sandbox."""

    def __init__(
        self,
        llm_proxy: LLMProxy,
        sandbox: Sandbox,
        storage: ObjectStorageClient,
    ) -> None:
        super().__init__("ToolSmith")
        self.llm_proxy = llm_proxy
        self.sandbox = sandbox
        self.storage = storage

    def execute(self, context: AgentContext) -> AgentResponse:
        specification = context.payload.get("tool_spec") or context.goal
        test_snippet = context.payload.get("test_snippet")

        code = self._generate_tool(specification)
        result = None
        success = True
        if test_snippet:
            combined = f"{code}\n\nif __name__ == '__main__':\n{test_snippet}"
            result = self.sandbox.run_sync(combined)
            success = result.success

        artifact = None
        if context.payload.get("persist_tool"):
            key = f"{context.task_id}/tools/{context.payload.get('tool_name', 'tool')}.py"
            self.storage.ensure_bucket()
            self.storage.upload_bytes(key, code.encode("utf-8"), content_type="text/x-python")
            artifact = AgentArtifact(uri=key, description="Generated tool", media_type="text/x-python")

        return AgentResponse(
            success=success,
            output={
                "code": code,
                "test": _sandbox_to_dict(result),
            },
            message="ToolSmith generated tool" if success else "ToolSmith encountered errors",
            artifacts=[artifact] if artifact else [],
        )

    def _generate_tool(self, specification: str) -> str:
        prompt = (
            "Create a reusable Python utility function matching the specification below. "
            "Ensure it is pure and contains docstrings.\n"
            f"Specification: {specification}"
        )
        response = self.llm_proxy.complete(LLMRequest(prompt=prompt, temperature=0.2))
        lines = []
        record = False
        for line in response.splitlines():
            if line.strip().startswith(("```python", "```")):
                record = not record
                continue
            if record:
                lines.append(line)
        code = "\n".join(lines).strip()
        return code or "def generated_tool(*args, **kwargs):\n    \"\"\"Fallback tool.\"\"\"\n    return None\n"


def _sandbox_to_dict(result: Optional):
    if result is None:
        return None
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.return_code,
        "error": result.error,
    }
