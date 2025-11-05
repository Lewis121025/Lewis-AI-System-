"""Redis-backed task queue helpers using RQ."""

from __future__ import annotations

import logging
from typing import Optional

import redis
from rq import Queue
from rq.exceptions import NoSuchJobError

from app.config import get_settings

LOGGER = logging.getLogger(__name__)

_REDIS_CONN: dict[str, redis.Redis] = {}
_QUEUE: Optional[Queue] = None
_DEAD_LETTER_QUEUE: Optional[Queue] = None


def get_redis_connection(url: Optional[str] = None) -> redis.Redis:
    """Return a cached Redis connection."""
    settings = get_settings()
    redis_url = url or settings.redis_url
    if redis_url not in _REDIS_CONN:
        _REDIS_CONN[redis_url] = redis.Redis.from_url(
            redis_url, decode_responses=True
        )
    return _REDIS_CONN[redis_url]


def get_queue(name: str = "orchestrator") -> Queue:
    """Return the primary RQ queue used by agents."""
    global _QUEUE
    if _QUEUE is None:
        _QUEUE = Queue(name, connection=get_redis_connection())
    return _QUEUE


def get_dead_letter_queue(name: str = "orchestrator-dlq") -> Queue:
    """Return the dead-letter queue for failed jobs."""
    global _DEAD_LETTER_QUEUE
    if _DEAD_LETTER_QUEUE is None:
        settings = get_settings()
        redis_url = settings.redis_dlq_url or settings.redis_url
        connection = get_redis_connection(redis_url)
        _DEAD_LETTER_QUEUE = Queue(name, connection=connection)
    return _DEAD_LETTER_QUEUE


def enqueue_job(func, *args, queue_name: str = "orchestrator", **kwargs):
    """Enqueue a callable into the queue and return the RQ job."""
    queue = get_queue(queue_name)
    job = queue.enqueue(func, *args, **kwargs)
    LOGGER.debug("Enqueued job %s on queue %s", job.id, queue.name)
    return job


def fetch_job(job_id: str, queue_name: str = "orchestrator"):
    """Retrieve a job by ID."""
    queue = get_queue(queue_name)
    try:
        return queue.fetch_job(job_id)
    except NoSuchJobError:
        LOGGER.warning("Job %s not found on queue %s", job_id, queue_name)
        return None
