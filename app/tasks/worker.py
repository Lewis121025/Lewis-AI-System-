"""RQ Worker 启动入口，负责消费编排器任务队列。"""

from rq import Queue, Worker
from rq.connections import Connection

from app.infrastructure.redis_queue import get_queue, get_redis_connection
from app.orchestrator.orchestrator import process_task_job


def run_worker(queue_name: str = "orchestrator") -> None:
    """启动监听指定队列的 RQ Worker。"""
    connection = get_redis_connection()
    with Connection(connection):
        worker = Worker([Queue(queue_name, connection=connection)])
        worker.work()


__all__ = ["run_worker", "process_task_job"]
