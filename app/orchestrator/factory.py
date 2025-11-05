"""编排器工厂方法：集中构建各智能体与依赖的实例。"""

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
    """创建单例编排器，避免重复初始化底层资源。"""
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
