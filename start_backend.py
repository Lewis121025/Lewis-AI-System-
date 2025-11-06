#!/usr/bin/env python
"""快速启动 FastAPI 后端服务的脚本。

使用方式：
    python start_backend.py

默认配置：
    - Host: 127.0.0.1
    - Port: 8002
    - 热重载已启用
"""

import sys

try:
    import uvicorn
except ImportError:
    print("错误: 未找到 uvicorn。请运行: pip install uvicorn[standard]")
    sys.exit(1)


def main():
    """启动 FastAPI 应用服务器。"""
    print("=" * 60)
    print("🚀 正在启动 Lewis AI System 后端服务...")
    print("=" * 60)
    print("📍 地址: http://127.0.0.1:8002")
    print("📖 API 文档: http://127.0.0.1:8002/docs")
    print("🔄 热重载: 已启用")
    print("=" * 60)
    print()

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)

