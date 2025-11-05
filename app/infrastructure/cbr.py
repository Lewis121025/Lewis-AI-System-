"""Case-Based Reasoning service."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from sqlalchemy import select

from app.infrastructure.db import get_session
from app.models.entities import ExperienceRecord
from app.models.enums import ExperienceKind

LOGGER = logging.getLogger(__name__)


def _cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class RetrievedCase:
    """Structured result for similar case lookups."""

    reference_id: str
    kind: ExperienceKind
    title: str
    metadata: dict
    score: float


class CBRService:
    """Case-Based Reasoning repository."""

    def __init__(
        self,
        embedder: Callable[[str], list[float]],
    ) -> None:
        self._embedder = embedder

    def add_experience(
        self,
        reference_id: str,
        kind: ExperienceKind,
        title: str,
        content: str,
        metadata: Optional[dict] = None,
        embedding: Optional[list[float]] = None,
    ) -> ExperienceRecord:
        """Persist a new experience case."""
        embedding = embedding or self._embedder(content)
        payload = metadata or {}
        with get_session() as session:
            record = ExperienceRecord(
                reference_id=reference_id,
                kind=kind,
                title=title,
                metadata=payload,
                embedding=embedding,
            )
            session.add(record)
            session.flush()
            LOGGER.info("Stored experience %s (%s)", reference_id, kind)
            return record

    def find_similar(
        self,
        query: str,
        kind: Optional[ExperienceKind] = None,
        limit: int = 3,
    ) -> list[RetrievedCase]:
        """Return similar cases ordered by cosine similarity."""
        query_embedding = self._embedder(query)
        with get_session() as session:
            stmt = select(ExperienceRecord)
            if kind:
                stmt = stmt.where(ExperienceRecord.kind == kind)
            records = session.scalars(stmt).all()

        scored: list[RetrievedCase] = []
        for record in records:
            if not record.embedding:
                continue
            score = _cosine_similarity(query_embedding, record.embedding)
            scored.append(
                RetrievedCase(
                    reference_id=record.reference_id,
                    kind=record.kind,
                    title=record.title,
                    metadata=record.metadata,
                    score=score,
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]
