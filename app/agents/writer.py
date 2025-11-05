"""Writer（执行）智能体：根据计划编写代码或文本，并可在沙箱中验证。"""

from __future__ import annotations

import textwrap
from typing import Optional

from app.agents.base import Agent, AgentArtifact, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.agents.sandbox import Sandbox, SandboxResult
from app.infrastructure.storage import ObjectStorageClient


class WriterAgent(Agent):
    """负责将规划后的步骤转化为具体实现结果。"""

    def __init__(
        self,
        llm_proxy: LLMProxy,
        sandbox: Sandbox,
        storage: ObjectStorageClient,
    ) -> None:
        super().__init__("Writer")
        self.llm_proxy = llm_proxy
        self.sandbox = sandbox
        self.storage = storage

    def execute(self, context: AgentContext) -> AgentResponse:
        instructions = context.payload.get("task") or context.goal
        code = self._generate_code(instructions, context.payload)
        sandbox_result: Optional[SandboxResult] = None
        if context.payload.get("run_in_sandbox", True):
            sandbox_result = self.sandbox.run_sync(code)

        output = {
            "code": code,
            "sandbox": _sandbox_result_to_dict(sandbox_result),
        }

        artifact_uri = None
        if context.payload.get("persist_code"):
            key = f"{context.task_id}/writer_step.py"
            self.storage.ensure_bucket()
            self.storage.upload_bytes(key, code.encode("utf-8"), content_type="text/x-python")
            artifact_uri = key

        artifacts = []
        if artifact_uri:
            artifacts.append(
                AgentArtifact(
                    uri=artifact_uri,
                    description="Generated code artifact",
                    media_type="text/x-python",
                )
            )

        return AgentResponse(
            success=True if (sandbox_result is None or sandbox_result.success) else False,
            output=output,
            message="Writer execution completed",
            artifacts=artifacts,
        )

    def _generate_code(self, instructions: str, payload: dict) -> str:
        if payload.get("code_override"):
            return payload["code_override"]
        prompt = textwrap.dedent(
            f"""
            You are the Writer agent. Generate Python code to accomplish the task below.
            Ensure the code is self-contained and uses standard library only.
            Task: {instructions}
            """
        ).strip()
        response = self.llm_proxy.complete(
            LLMRequest(prompt=prompt, temperature=0.1, model=None)
        )
        code_lines = []
        record = False
        for line in response.splitlines():
            if line.strip().startswith(("```python", "```")):
                record = not record
                continue
            if record:
                code_lines.append(line)
        generated = "\n".join(code_lines).strip()
        return generated or "print('Task executed by Writer agent')"


def _sandbox_result_to_dict(result: Optional[SandboxResult]) -> Optional[dict]:
    if result is None:
        return None
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "return_code": result.return_code,
        "error": result.error,
    }
