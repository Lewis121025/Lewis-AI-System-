# Lewis 的第一个项目——自治三层 AI 系统

本仓库实现了“Lewis 的第一个项目”提出的三层智能系统：

- **L1：Streamlit 指挥中心（ui/app.py）** – 负责收集用户目标、发起任务、轮询状态并展示事件日志。
- **L2：FastAPI 网关（app/main.py 与 app/api）** – 暴露 REST/WebSocket 接口，处理鉴权，并与编排器交互。
- **L3：认知智能体层（app/agents）** – 感知、规划、写作、视觉、工具锻造、评审、LLM 代理与沙箱等智能体协同完成任务。

系统依赖 PostgreSQL + pgvector 保存状态与案例、Redis/RQ 提供任务队列、MinIO/S3 存储工件，并通过 OpenTelemetry 输出日志与链路追踪。

## 架构总览

```
Streamlit UI (L1) --> FastAPI Gateway (L2) --> Task Orchestrator & Agents (L3)
                                |            \-- Redis Queue (RQ)
                                |            \-- PostgreSQL + pgvector
                                |            \-- MinIO / S3 对象存储
                                |            \-- OpenTelemetry 追踪与日志
```

- **Streamlit 前端**：提交高层目标、展示进度与结果。
- **FastAPI 层**：任务创建、状态查询、事件流、健康检查与鉴权。
- **智能体与编排器**：感知→规划→执行→评审闭环，执行轨迹写入经验库。
- **支持组件**：Redis 队列、PostgreSQL/pgvector、MinIO/S3、OpenTelemetry。

## 目录结构

```
app/
├── agents/            # 各类智能体、LLM 代理与沙箱
├── api/               # FastAPI 路由与依赖注入
├── config.py          # 基于 Pydantic 的集中配置
├── infrastructure/    # 数据库、Redis、对象存储、CBR、遥测
├── main.py            # FastAPI 应用工厂
├── models/            # SQLAlchemy 模型（任务、事件、经验、工件）
├── orchestrator/      # 任务编排器与构建工厂
├── schemas/           # Pydantic 请求/响应模型
└── tasks/             # RQ worker 启动脚本
ui/
└── app.py             # Streamlit 指挥中心
```

测试位于 `tests/`，覆盖智能体逻辑、编排流程、API 以及沙箱。

## 前置要求

- Python 3.10 及以上
- PostgreSQL 14+ 并启用 `pgvector`
- Redis 6+（用于 RQ 队列）
- MinIO 或任意 S3 兼容对象存储（可选）
- （可选）Grafana Agent / OTLP Collector 用于接收遥测数据

## 安装步骤

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 配置说明

配置由 `.env` 或环境变量加载，可在 `app/config.py` 查看全部字段。常用变量：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `API_TOKEN` | FastAPI/Streamlit 访问令牌 | `change-me` |
| `DATABASE_URL` | SQLAlchemy 连接串 | `postgresql+psycopg2://postgres:postgres@localhost:5432/lewis` |
| `REDIS_URL` | Redis 地址 | `redis://localhost:6379/0` |
| `S3_ENDPOINT_URL` 等 | MinIO/S3 相关配置 | 无 |
| `OTLP_ENDPOINT` | OTLP 导出端点 | 无 |
| `OPENAI_API_KEY` 等 | LLM API 密钥 | 无 |

## 数据库初始化

1. 在 PostgreSQL 中启用扩展：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. 首次运行 FastAPI 应用或调用 `app.infrastructure.db.init_db()` 将自动建表。

## 运行指引

1. **启动 FastAPI 后端**
   ```bash
   uvicorn app.main:app --reload
   ```
2. **启动 RQ worker**（新终端）
   ```bash
   python -m rq worker orchestrator --with-scheduler --path .
   # 或使用封装入口
   python -c "from app.tasks.worker import run_worker; run_worker()"
   ```
3. **启动 Streamlit UI**
   ```bash
   streamlit run ui/app.py
   ```
4. （可选）配置 `OTLP_ENDPOINT` 并在 Grafana/Loki 中接入追踪与日志。

## 测试

项目提供 pytest 用例：

```bash
python -m pytest
```

若尚未安装 pytest，请先执行 `pip install -r requirements.txt`。测试基于 SQLite 与同步模式，无需真实的 Redis/PostgreSQL 环境。

## 主要模块亮点

- **LLM Proxy**：统一封装 OpenAI/Anthropic/Gemini 等提供商，未配置密钥时自动回退到可测试的离线响应。
- **Sandbox**：在独立子进程执行 Python 代码，支持超时控制，可根据生产需求强化隔离策略。
- **CBR 案例库**：将执行计划写入经验库，后续任务可按向量相似度检索历史方案。
- **Telemetry**：预置结构化日志与 OpenTelemetry 跟踪，便于接入 Grafana/Loki/Tempo。

## 安全与扩展建议

- 替换默认 `API_TOKEN`，保护接口安全。
- 将沙箱运行在容器/虚拟机中，避免执行不可信代码的风险。
- 为 Redis、PostgreSQL、对象存储启用身份验证与 TLS。
- 通过机密管理服务注入 LLM API 密钥，避免写入代码库。

后续可探索的方向：

1. 扩展分布式执行能力，引入多 worker/多智能体协作。
2. 对 ToolSmith 生成的工具做持久化及自动注册。
3. 在 PostgreSQL 中直接执行向量相似度查询，提升检索效率。
4. Streamlit UI 接入 WebSocket 实时推送与更丰富的可视化。
5. 扩展测试覆盖率，并与真实外部服务做契约/集成测试。

---

欢迎继续在此基础上迭代与实验。
