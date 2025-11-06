"""Writer（执行）智能体：根据计划编写代码或文本，并可在沙箱中验证。"""

from __future__ import annotations

import ast
import re
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
        if arithmetic_code := self._maybe_generate_arithmetic_code(instructions, payload):
            return arithmetic_code
        if payload.get("code_override"):
            return payload["code_override"]
        prompt = textwrap.dedent(
            f"""
            You are the Writer agent. Generate Python code to accomplish the task below.
            Ensure the code is self-contained, uses standard library only, and return the code
            inside a markdown code block in the format ```python ... ```.
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
        if generated:
            return generated
        # Fallback：若模型未按要求返回代码，则提供最小可执行模板，保留执行上下文。
        return textwrap.dedent(
            f"""
            print("Task description: {instructions}")
            """
        ).strip()

    @staticmethod
    def _sanitize_expression(source: str) -> Optional[str]:
        candidate = re.sub(r"[^0-9\\+\\-\\*/\\.\\(\\)\\s]", "", source).strip()
        if not candidate:
            return None
        try:
            tree = ast.parse(candidate, mode="eval")
        except SyntaxError:
            return None

        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Num,
            ast.Constant,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.Mod,
            ast.Pow,
            ast.FloorDiv,
            ast.USub,
            ast.UAdd,
            ast.Load,
        )

        for node in ast.walk(tree):
            if not isinstance(node, allowed_nodes):
                return None
            if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
                return None
        return candidate

    def _maybe_generate_arithmetic_code(self, instructions: str, payload: dict) -> Optional[str]:
        expression = payload.get("expression")
        if not expression:
            if any(op in instructions for op in "+-*/") and any(char.isdigit() for char in instructions):
                expression = self._sanitize_expression(instructions)
            else:
                expression = None
        else:
            expression = self._sanitize_expression(expression)

        if not expression:
            return None

        escaped_expr = expression.replace("\\", "\\\\").replace('"', '\\"')
        return textwrap.dedent(
            f"""
            import ast
            import operator

            _BINARY_OPS = {{
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.FloorDiv: operator.floordiv,
                ast.Mod: operator.mod,
                ast.Pow: operator.pow,
            }}

            _UNARY_OPS = {{
                ast.UAdd: operator.pos,
                ast.USub: operator.neg,
            }}

            def _eval_expr(node):
                if isinstance(node, ast.Expression):
                    return _eval_expr(node.body)
                if isinstance(node, ast.Constant):
                    return node.value
                if isinstance(node, ast.Num):  # pragma: no cover - legacy Py<3.8
                    return node.n
                if isinstance(node, ast.BinOp):
                    op_type = type(node.op)
                    if op_type not in _BINARY_OPS:
                        raise ValueError("Unsupported binary operation")
                    return _BINARY_OPS[op_type](_eval_expr(node.left), _eval_expr(node.right))
                if isinstance(node, ast.UnaryOp):
                    op_type = type(node.op)
                    if op_type not in _UNARY_OPS:
                        raise ValueError("Unsupported unary operation")
                    return _UNARY_OPS[op_type](_eval_expr(node.operand))
                raise ValueError("Unsupported expression element")

            def evaluate(expression: str):
                tree = ast.parse(expression, mode="eval")
                return _eval_expr(tree)

            expression = "{escaped_expr}"
            result = evaluate(expression)
            print("表达式:", expression)
            print("结果:", result)
            """
        ).strip()


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
