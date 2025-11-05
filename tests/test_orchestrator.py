import os

import pytest

from app.agents.art_director import ArtDirectorAgent
from app.agents.critic import CriticAgent
from app.agents.llm_proxy import LLMProxy
from app.agents.perceptor import PerceptorAgent
from app.agents.planner import PlannerAgent
from app.agents.sandbox import Sandbox
from app.agents.toolsmith import ToolSmithAgent
from app.agents.writer import WriterAgent
from app.config import reset_settings_cache
from app.infrastructure.cbr import CBRService
from app.infrastructure.db import init_db
from app.orchestrator.orchestrator import TaskOrchestrator


class DummyStorage:
    def __init__(self):
        self.objects = {}

    def ensure_bucket(self):
        return None

    def upload_bytes(self, key, data, **kwargs):
        self.objects[key] = data
        return key


@pytest.fixture(scope="module", autouse=True)
def setup_db(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("orch_db")
    db_path = db_dir / "orchestrator.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    reset_settings_cache()
    init_db(create_extensions=False)
    yield


def build_orchestrator_for_test():
    llm_proxy = LLMProxy()
    sandbox = Sandbox(timeout=3)
    storage = DummyStorage()
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
        enable_queue=False,
    )


def test_orchestrator_executes_pipeline():
    orchestrator = build_orchestrator_for_test()
    task_id = orchestrator.start_task("Build a reporting dashboard", sync=True)
    status = orchestrator.get_status(task_id)
    assert status is not None
    assert status["status"] == "completed"
    events = orchestrator.list_events(task_id)
    event_types = [event["event_type"] for event in events]
    assert "perception_completed" in event_types
    assert "planning_completed" in event_types
    assert any(evt.startswith("writer_") for evt in event_types)
