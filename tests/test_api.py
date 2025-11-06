"""FastAPI 接口测试：验证鉴权与任务生命周期。"""

import os

import pytest
from fastapi.testclient import TestClient

from app.agents.art_director import ArtDirectorAgent
from app.agents.critic import CriticAgent
from app.agents.llm_proxy import LLMProxy
from app.agents.perceptor import PerceptorAgent
from app.agents.planner import PlannerAgent
from app.agents.sandbox import Sandbox
from app.agents.toolsmith import ToolSmithAgent
from app.agents.writer import WriterAgent
from app.api.dependencies import get_orchestrator
from app.config import reset_settings_cache
from app.infrastructure.cbr import CBRService
from app.infrastructure.db import init_db
from app.orchestrator.orchestrator import TaskOrchestrator
from app.main import create_app


class DummyStorage:
    """用于 API 测试的对象存储替身。"""

    def ensure_bucket(self):
        return None

    def upload_bytes(self, key, data, **kwargs):
        return key


@pytest.fixture(scope="module")
def test_client(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("api_db")
    db_path = db_dir / "api.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["API_TOKEN"] = "test-token"
    os.environ["OPENROUTER_API_KEY"] = ""
    reset_settings_cache()
    init_db(create_extensions=False)

    llm_proxy = LLMProxy()
    sandbox = Sandbox(timeout=3)
    storage = DummyStorage()
    cbr_service = CBRService(embedder=llm_proxy.embed_text)

    orchestrator = TaskOrchestrator(
        perceptor=PerceptorAgent(llm_proxy),
        planner=PlannerAgent(llm_proxy, cbr_service),
        writer=WriterAgent(llm_proxy, sandbox, storage),
        art_director=ArtDirectorAgent(llm_proxy, storage),
        toolsmith=ToolSmithAgent(llm_proxy, sandbox, storage),
        critic=CriticAgent(llm_proxy),
        cbr_service=cbr_service,
        enable_queue=False,
    )

    app = create_app()
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    client = TestClient(app)
    yield client


def test_task_lifecycle(test_client):
    response = test_client.post(
        "/tasks",
        json={"goal": "Generate a report", "sync": True},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    status_resp = test_client.get(
        f"/tasks/{task_id}", headers={"Authorization": "Bearer test-token"}
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in {"completed", "failed"}

    events_resp = test_client.get(
        f"/tasks/{task_id}/events", headers={"Authorization": "Bearer test-token"}
    )
    assert events_resp.status_code == 200
    assert isinstance(events_resp.json(), list)


def test_authentication_required(test_client):
    response = test_client.post("/tasks", json={"goal": "Test", "sync": True})
    assert response.status_code == 403 or response.status_code == 401
