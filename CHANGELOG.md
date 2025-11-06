# 更新日志 (Changelog)

本文档记录项目的所有重要变更。

## [未发布] - 2024-11-06

### ✅ 修复

- **端口配置统一**: 修复了 UI 和后端端口配置不一致的问题
  - UI (`ui/app.py`) 默认连接端口从 8000 更新为 8002
  - README 中的运行指引添加了明确的端口参数
  
- **废弃 API 更新**: 替换了 FastAPI 和 Python 中的废弃 API
  - 使用 `lifespan` 替代废弃的 `@app.on_event("startup")` 装饰器
  - 使用 `datetime.now(UTC)` 替代废弃的 `datetime.utcnow()`
  - 减少了测试警告数量从 9 个降至 1 个

### ✨ 优化

- **应用生命周期管理**: 改进了资源管理和清理逻辑
  - 使用 `asynccontextmanager` 提供更好的启动/关闭钩子
  - 添加了应用关闭时的日志记录
  
- **类型注解**: 改进了类型提示的准确性
  - 为 `lifespan` 函数添加了 `AsyncGenerator` 类型注解
  
- **文档更新**: 
  - README 中的运行指引更加明确
  - 添加了快速启动脚本 `start_backend.py`
  - 创建了本变更日志

### 🧪 测试

- ✅ 所有 9 个测试用例通过
- ✅ 无 linter 错误
- ✅ 减少了 8 个废弃 API 警告

---

## [0.1.0] - 初始版本

### 功能特性

- 🏗️ 三层 AI 系统架构（L1: Streamlit UI, L2: FastAPI Gateway, L3: Agent Layer）
- 🤖 6 个认知智能体（Perceptor, Planner, Writer, ArtDirector, ToolSmith, Critic）
- 💾 PostgreSQL + pgvector 支持向量搜索
- 🔄 Redis + RQ 异步任务队列
- 📦 S3/MinIO 对象存储集成
- 📊 OpenTelemetry 可观测性支持
- 🧠 CBR（案例推理）经验库系统
- 🔒 沙箱代码执行环境
- 🧪 完整的测试覆盖
- 📚 详细的中文文档

