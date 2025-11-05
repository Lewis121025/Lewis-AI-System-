"""智能体基类与通用结构定义。
Provides foundational dataclasses and abstract base class for all agents.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentContext:
    """Agent 执行上下文。

    Attributes
    ----------
    task_id:
        当前任务的唯一标识，便于追踪日志与状态。
    goal:
        用户或上游模块的总体目标描述。
    payload:
        针对具体步骤的附加参数，通常由编排器传入。
    prior_outputs:
        其他智能体已产出的结果，可供当前智能体参考。
    """

    task_id: str
    goal: str
    payload: dict[str, Any] = field(default_factory=dict)
    prior_outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentArtifact:
    """智能体生成的工件信息，例如文件、图表等。"""

    uri: Optional[str]
    description: str
    media_type: str = "text/plain"


@dataclass
class AgentResponse:
    """智能体执行结果的统一结构。"""

    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    message: str = ""
    artifacts: list[AgentArtifact] = field(default_factory=list)


class AgentError(RuntimeError):
    """当智能体无法完成任务时抛出该异常。"""


class Agent(ABC):
    """所有智能体的抽象基类，定义统一的 execute 接口。"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.logger = logging.getLogger(f"agents.{self.name.lower()}")

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentResponse:
        """执行智能体逻辑，必须由子类实现。"""
