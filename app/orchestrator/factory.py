"""编排器工厂方法：集中构建各智能体与依赖的实例。"""

from functools import lru_cache

from app.agents.art_director import ArtDirectorAgent
from app.agents.critic import CriticAgent
from app.agents.llm_proxy import LLMProxy
from app.agents.perceptor import PerceptorAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.sandbox import Sandbox
from app.agents.search_tool import GoogleSearchTool
from app.agents.toolsmith import ToolSmithAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.weather_api import WeatherAPITool
from app.agents.writer import WriterAgent
from app.infrastructure.cbr import CBRService
from app.infrastructure.storage import ObjectStorageClient
from app.orchestrator.langgraph_orchestrator import LangGraphOrchestrator

# 全局编排器实例
_orchestrator = None

def build_orchestrator() -> LangGraphOrchestrator:
    """创建编排器实例，支持动态重建以应用代码更新。"""
    global _orchestrator
    
    # 开发模式下每次重新创建，生产模式使用单例
    import os
    if os.getenv("ENVIRONMENT", "development") == "development" or _orchestrator is None:
        llm_proxy = LLMProxy()
        sandbox = Sandbox()
        storage = ObjectStorageClient()
        cbr_service = CBRService(embedder=llm_proxy.embed_text)
        search_tool = GoogleSearchTool()
        weather_tool = WeatherAPITool()

        perceptor = PerceptorAgent(llm_proxy)
        planner = PlannerAgent(llm_proxy, cbr_service)
        writer = WriterAgent(llm_proxy, sandbox, storage)
        art_director = ArtDirectorAgent(llm_proxy, storage)
        toolsmith = ToolSmithAgent(llm_proxy, sandbox, storage)
        researcher = ResearcherAgent(search_tool, llm_proxy)
        weather = WeatherAgent(weather_tool, llm_proxy)
        critic = CriticAgent(llm_proxy)

        # 检查 Redis 是否可用，决定是否启用队列
        enable_queue = _check_redis_available()
        
        _orchestrator = LangGraphOrchestrator(
            perceptor=perceptor,
            planner=planner,
            writer=writer,
            art_director=art_director,
            toolsmith=toolsmith,
            researcher=researcher,
            weather=weather,
            critic=critic,
            cbr_service=cbr_service,
            enable_queue=enable_queue,
        )
        
    return _orchestrator


def _check_redis_available() -> bool:
    """检查 Redis 是否可用。"""
    try:
        from app.config import get_settings
        from app.infrastructure.redis_queue import get_redis_connection
        settings = get_settings()
        if not settings.redis_url:
            return False
        # 尝试连接 Redis
        conn = get_redis_connection()
        conn.ping()
        return True
    except Exception:
        return False


def reset_orchestrator_cache() -> None:
    """重置编排器缓存，强制重新创建实例。"""
    global _orchestrator
    _orchestrator = None
