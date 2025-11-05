"""RQ worker entry point for processing orchestrator jobs."""

from rq import Connection, Queue, Worker

from app.infrastructure.redis_queue import get_queue, get_redis_connection
from app.orchestrator.orchestrator import process_task_job


def run_worker(queue_name: str = "orchestrator") -> None:
    """Start an RQ worker listening on the orchestrator queue."""
    connection = get_redis_connection()
    with Connection(connection):
        worker = Worker([Queue(queue_name, connection=connection)])
        worker.work()


__all__ = ["run_worker", "process_task_job"]
