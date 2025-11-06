"""LLM 代理模块：负责在不同大模型服务商之间进行路由。

兼容 OpenAI、OpenRouter 等服务，并在无法访问外部 API 时提供离线降级。
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from typing import Optional

import requests

from app.config import get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """LLM 请求的归一化结构，用于在不同提供商之间复用参数。"""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.2
    system_prompt: Optional[str] = None


class LLMProxy:
    """统一的大语言模型调用接口，可根据配置自动选择提供商。"""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._openai_client = None

    def _ensure_openai(self):
        if self._openai_client is not None:
            return self._openai_client
        if not self.settings.openai_api_key:
            raise RuntimeError("OpenAI API key not configured.")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("openai package is required for OpenAI provider.") from exc
        self._openai_client = OpenAI(api_key=self.settings.openai_api_key)
        return self._openai_client

    def complete(self, request: LLMRequest) -> str:
        """根据配置路由补全请求，优先使用高可用的提供商。"""
        provider = (request.provider or self.settings.default_llm_provider).lower()
        if provider == "openai" and self.settings.openai_api_key:
            return self._complete_openai(request)
        if provider == "openrouter" and self.settings.openrouter_api_key:
            return self._complete_openrouter(request)
        LOGGER.debug(
            "Falling back to offline completion for provider %s", provider
        )
        return self._offline_completion(request.prompt)

    def embed_text(self, text: str, model: Optional[str] = None) -> list[float]:
        """返回文本向量表示，若无可用服务则使用哈希模拟向量。"""
        provider = self.settings.default_llm_provider.lower()
        if provider == "openai" and self.settings.openai_api_key:
            return self._embed_openai(text, model)
        return self._offline_embedding(text)

    # --- Provider implementations -------------------------------------------------

    def _complete_openai(self, request: LLMRequest) -> str:
        client = self._ensure_openai()
        model = request.model or "gpt-4o-mini"
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=request.temperature,
                messages=[
                    {"role": "system", "content": request.system_prompt or ""},
                    {"role": "user", "content": request.prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # pragma: no cover - network
            LOGGER.exception("OpenAI request failed: %s", exc)
            return self._offline_completion(request.prompt)

    def _embed_openai(self, text: str, model: Optional[str] = None) -> list[float]:
        client = self._ensure_openai()
        embed_model = model or "text-embedding-3-large"
        try:
            response = client.embeddings.create(model=embed_model, input=text)
            return list(response.data[0].embedding)
        except Exception as exc:  # pragma: no cover - network
            LOGGER.exception("OpenAI embedding failed: %s", exc)
            return self._offline_embedding(text)

    def _complete_openrouter(self, request: LLMRequest) -> str:
        """通过 OpenRouter 聚合平台发起聊天补全请求。"""
        model = request.model or self.settings.openrouter_default_model
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Lewis AI Command Center",
        }
        payload = {
            "model": model,
            "temperature": request.temperature,
            "messages": [],
        }
        if request.system_prompt:
            payload["messages"].append(
                {"role": "system", "content": request.system_prompt}
            )
        payload["messages"].append({"role": "user", "content": request.prompt})
        base_url = self.settings.openrouter_base_url.rstrip("/")
        url = f"{base_url}/chat/completions"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            return message
        except Exception as exc:  # pragma: no cover - network
            LOGGER.exception("OpenRouter request failed: %s", exc)
            return self._offline_completion(request.prompt)

    # --- Offline fallbacks --------------------------------------------------------

    @staticmethod
    def _offline_completion(prompt: str) -> str:
        """Deterministic local completion used for tests/offline mode."""
        snippet = prompt.strip().split("\n")[0][:180]
        return (
            "Offline completion (mock LLM)."
            f" Echo of prompt head: {snippet}"
        )

    @staticmethod
    def _offline_embedding(text: str, dimensions: int = 1536) -> list[float]:
        """Deterministic hash-based embedding matching production vector size."""
        seed = text.encode("utf-8")
        raw_values: list[float] = []
        counter = 0
        while len(raw_values) < dimensions:
            counter_bytes = counter.to_bytes(4, "little", signed=False)
            digest = hashlib.sha256(seed + counter_bytes).digest()
            raw_values.extend(byte / 255.0 for byte in digest)
            counter += 1
        vector = raw_values[:dimensions]
        norm = math.sqrt(sum(val * val for val in vector))
        if norm == 0:
            return [0.0 for _ in range(dimensions)]
        return [val / norm for val in vector]
