"""智能体层单元测试，验证感知/规划/执行等核心行为。"""

import os

import pytest

from app.agents.base import AgentContext
from app.agents.critic import CriticAgent
from app.agents.llm_proxy import LLMProxy, LLMRequest
from app.agents.perceptor import PerceptorAgent
from app.agents.planner import PlannerAgent
from app.agents.sandbox import Sandbox
from app.agents.writer import WriterAgent
from app.infrastructure.cbr import CBRService
from app.infrastructure.db import init_db
from app.models.enums import ExperienceKind
from app.config import reset_settings_cache


class DummyStorage:
    """测试替身：模拟对象存储，避免真实外部依赖。"""

    def __init__(self):
        self.data = {}

    def ensure_bucket(self):
        return None

    def upload_bytes(self, key, content, **kwargs):
        self.data[key] = content
        return key


@pytest.fixture(scope="module", autouse=True)
def configure_sqlite(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "lewis_test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.as_posix()}"
    os.environ["OPENROUTER_API_KEY"] = ""
    reset_settings_cache()
    init_db(create_extensions=False)
    yield


@pytest.fixture()
def llm_proxy():
    return LLMProxy()


def test_llm_proxy_offline_mode(llm_proxy):
    response = llm_proxy.complete(LLMRequest(prompt="Hello world"))
    assert "Offline completion" in response


def test_perceptor_returns_task_list(llm_proxy):
    agent = PerceptorAgent(llm_proxy)
    goal = "- Collect requirements\n- Build prototype\n- Test and iterate"
    ctx = AgentContext(task_id="t1", goal=goal)
    response = agent.execute(ctx)
    assert response.success
    assert len(response.output["tasks"]) == 3


def test_planner_generates_plan(llm_proxy):
    cbr = CBRService(embedder=llm_proxy.embed_text)
    cbr.add_experience(
        reference_id="case-1",
        kind=ExperienceKind.PLAN,
        title="Sample plan",
        content="Plan for building web apps",
        metadata={"insight": "Reuse API scaffolding"},
    )
    agent = PlannerAgent(llm_proxy, cbr)
    ctx = AgentContext(
        task_id="t2",
        goal="Build a dashboard",
        payload={
            "tasks": [
                "Design database schema",
                "Implement API endpoints",
                "Create Streamlit interface",
            ]
        },
    )
    response = agent.execute(ctx)
    assert response.success
    assert len(response.output["plan"]) >= 4
    assert "Final quality review" in response.output["plan"][-1]["description"]


def test_writer_runs_code_in_sandbox(llm_proxy):
    sandbox = Sandbox(timeout=3)
    storage = DummyStorage()
    agent = WriterAgent(llm_proxy, sandbox, storage)
    ctx = AgentContext(task_id="t3", goal="Print hello", payload={})
    response = agent.execute(ctx)
    assert response.success
    sandbox_result = response.output["sandbox"]
    assert sandbox_result["success"] is True
    assert sandbox_result["stdout"] is not None


def test_critic_provides_feedback(llm_proxy):
    agent = CriticAgent(llm_proxy)
    ctx = AgentContext(
        task_id="t4",
        goal="Review output",
        payload={"summary": "All tasks completed successfully."},
    )
    response = agent.execute(ctx)
    assert response.success
    assert response.output["verdict"] in {"approve", "request_changes"}
