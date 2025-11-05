"""ArtDirector（视觉）智能体：生成图像描述或简单图表。"""

from __future__ import annotations

import io
from typing import Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.agents.base import Agent, AgentArtifact, AgentContext, AgentResponse
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.infrastructure.storage import ObjectStorageClient


class ArtDirectorAgent(Agent):
    """负责处理与视觉相关的任务，如输出视觉简报或绘制图表。"""

    def __init__(self, llm_proxy: LLMProxy, storage: ObjectStorageClient) -> None:
        super().__init__("ArtDirector")
        self.llm_proxy = llm_proxy
        self.storage = storage

    def execute(self, context: AgentContext) -> AgentResponse:
        instructions = context.payload.get("task") or context.goal
        chart_data = context.payload.get("chart_data")

        artifact: Optional[AgentArtifact] = None
        description: str

        if chart_data:
            description, artifact = self._generate_chart(context.task_id, chart_data)
        else:
            description = self._generate_description(instructions)

        artifacts = [artifact] if artifact else []
        return AgentResponse(
            success=True,
            output={"description": description},
            message="ArtDirector completed visual task",
            artifacts=artifacts,
        )

    def _generate_description(self, instructions: str) -> str:
        prompt = (
            "You are the ArtDirector agent. Provide a concise visual brief describing "
            "what should be drawn or visualized for the following request:\n"
            f"{instructions}"
        )
        return self.llm_proxy.complete(LLMRequest(prompt=prompt, temperature=0.5))

    def _generate_chart(
        self, task_id: str, chart_data: dict
    ) -> tuple[str, Optional[AgentArtifact]]:
        figure, axes = plt.subplots()
        axes.plot(chart_data.get("x", []), chart_data.get("y", []), marker="o")
        axes.set_title(chart_data.get("title", "Generated Chart"))
        axes.set_xlabel(chart_data.get("x_label", "X"))
        axes.set_ylabel(chart_data.get("y_label", "Y"))
        figure.tight_layout()

        buffer = io.BytesIO()
        figure.savefig(buffer, format="png")
        plt.close(figure)
        buffer.seek(0)

        self.storage.ensure_bucket()
        key = f"{task_id}/art_director.png"
        self.storage.upload_bytes(
            key,
            buffer.read(),
            content_type="image/png",
            metadata={"generated-by": "ArtDirector"},
        )
        artifact = AgentArtifact(uri=key, description="Generated chart", media_type="image/png")
        return ("Chart generated and stored", artifact)
