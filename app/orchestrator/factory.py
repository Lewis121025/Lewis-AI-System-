"""Factory helpers to assemble orchestrator dependencies."""

from functools import lru_cache

from app.agents.art_director import ArtDirectorAgent
from app.agents.critic import CriticAgent
from app.agents.llm_proxy import LLMProxy
from app.agents.perceptor import PerceptorAgent
from app.agents.planner import PlannerAgent
from app.agents.sandbox import Sandbox
from app.agents.toolsmith import ToolSmithAgent
from app.agents.writer import WriterAgent
from app.infrastructure.cbr import CBRService
from app.infrastructure.storage import ObjectStorageClient
from app.orchestrator.orchestrator import TaskOrchestrator


@lru_cache(maxsize=1)
def build_orchestrator() -> TaskOrchestrator:
    llm_proxy = LLMProxy()
    sandbox = Sandbox()
    storage = ObjectStorageClient()
    cbr_service = CBRService(embedder=llm_proxy.embed_text)

    perceptor = PerceptorAgent(llm_proxy)
    planner = PlannerAgent(llm_proxy, cbr_service)
    writer = WriterAgent(llm_proxy, sandbox, storage)
    art_director = ArtDirectorAgent(llm_proxy, storage)
    toolsmith = ToolSmithAgent(llm_proxy, sandbox, storage)
    critic = CriticAgent(llm_proxy)

    return TaskOrchestrator(
        perceptor=perceptor,
        planner=planner,
        writer=writer,
        art_director=art_director,
        toolsmith=toolsmith,
        critic=critic,
        cbr_service=cbr_service,
    )
