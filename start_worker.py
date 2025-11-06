#!/usr/bin/env python
"""快速启动 RQ Worker 的脚本。

使用方式：
    python start_worker.py

功能：
    - 启动 RQ Worker 监听 orchestrator 队列
    - 处理异步任务执行
    - 需要 Redis 服务运行
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """启动 RQ Worker。"""
    print("=" * 60)
    print("Starting Lewis AI System Task Queue Worker...")
    print("=" * 60)
    print("Queue: orchestrator")
    print("Status: Listening...")
    print("=" * 60)
    print()
    print("[!] Note: Worker requires Redis service running")
    print("    If Redis is not running, please start Redis first")
    print("=" * 60)
    print()
    
    try:
        from app.tasks.worker import run_worker
        logger.info("Starting RQ worker for queue 'orchestrator'")
        run_worker()
    except KeyboardInterrupt:
        print("\n\nWorker stopped")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Failed to start worker: %s", exc)
        print("\n[X] Worker startup failed")
        print("\nPossible causes:")
        print("1. Redis service not running")
        print("2. Redis connection configuration error")
        print("3. Missing required Python packages")
        print("\nPlease check:")
        print("- Is Redis running: redis-cli ping")
        print("- Is REDIS_URL environment variable correctly configured")
        sys.exit(1)


if __name__ == "__main__":
    main()


