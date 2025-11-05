"""Language model proxy routing requests to different providers."""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from typing import Optional

from app.config import get_settings

LOGGER = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """Normalized representation of an LLM request."""

    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.2
    system_prompt: Optional[str] = None


class LLMProxy:
    """Route LLM calls through a unified interface."""

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
        """Route a completion request."""
        provider = (request.provider or self.settings.default_llm_provider).lower()
        if provider == "openai" and self.settings.openai_api_key:
            return self._complete_openai(request)
        LOGGER.debug(
            "Falling back to offline completion for provider %s", provider
        )
        return self._offline_completion(request.prompt)

    def embed_text(self, text: str, model: Optional[str] = None) -> list[float]:
        """Return embedding vector for provided text."""
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
    def _offline_embedding(text: str) -> list[float]:
        """Hash-based embedding to simulate vector output."""
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        # produce deterministic vector of length 32
        vector = [(byte / 255.0) for byte in digest[:32]]
        # normalize to unit length
        norm = math.sqrt(sum(val * val for val in vector))
        if norm == 0:
            return [0.0 for _ in vector]
        return [val / norm for val in vector]
