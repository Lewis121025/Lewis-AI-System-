# Lewis Trinity AI Platform

<div align="center">

**🤖 A Three-Layer Autonomous Multi-Agent System Based on LangGraph**

*Intelligent agents working together to solve complex tasks*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

</div>

---

## 📖 项目简介

**Lewis Trinity AI Platform** 是一个基于 LangGraph 的三层自治智能系统，通过多个专业智能体（Agents）协作完成复杂任务。系统采用"感知-规划-执行-评审"的完整闭环流程，支持智能搜索、天气查询、代码生成、报告撰写等多种任务类型。

### 💡 核心理念

- **三层架构分离**: UI层、API层、Agent层职责清晰，易于维护和扩展
- **智能体协作**: 多个专业Agent通过LangGraph状态机协同工作
- **闭环反馈**: 每个任务都经过感知→规划→执行→评审的完整流程
- **灵活扩展**: 可轻松添加新的Agent和功能模块

### 🏗️ 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  L1: Streamlit UI (用户界面层)                                │
│  - 任务提交与管理                                              │
│  - 实时状态监控                                                │
│  - 结果可视化展示                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  L2: FastAPI Gateway (API网关层)                             │
│  - RESTful API 接口                                           │
│  - 任务调度与编排                                              │
│  - 鉴权与日志追踪                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  L3: Agent Layer (智能体执行层)                               │
│  - Perceptor: 任务感知与理解                                   │
│  - Planner: 智能规划生成                                       │
│  - Researcher: 网络搜索                                        │
│  - Weather: 天气查询                                           │
│  - Writer: 代码生成与执行                                      │
│  - Critic: 质量评审                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ 核心特性

### 🎯 智能体系统
- **🔍 Researcher Agent**: 集成 Google Custom Search API，支持真实网络搜索
- **🌤️ Weather Agent**: 接入 WeatherAPI.com，提供实时天气数据
- **✍️ Writer Agent**: 智能代码生成，支持沙箱安全执行
- **📊 Planner Agent**: 任务智能分解，避免过度规划
- **✅ Critic Agent**: 质量评审，评分准确率 0.9+

### 🔧 技术栈
- **后端框架**: FastAPI + LangGraph
- **前端界面**: Streamlit (中文本地化)
- **数据存储**: PostgreSQL + pgvector (向量检索)
- **任务队列**: Redis + RQ
- **LLM支持**: OpenAI / gemini / Anthropic
- **监控追踪**: OpenTelemetry

---

## 🖼️ 运行实例

### 系统主界面
![系统主界面](screenshots/system-dashboard.gif)
*实时显示各个Agent的在线状态和系统配置*

### 任务执行示例

**任务 1: 天气分析**
![天气查询任务](screenshots/task-weather.gif)
*查询杭州近日天气，智能分析明天是否需要带伞*

**任务 2: GDP经济分析**  
![经济分析报告](screenshots/task-economy.gif)
*对比日韩GDP数据，生成300字markdown格式分析报告*

系统能够自动调用相应的智能体，完成从数据获取、分析到报告生成的全流程。任务评分达到 **0.90/1.0**。

---

## 🔄 系统运行逻辑

### 完整任务执行流程

```
用户提交任务
    ↓
1. Perceptor（感知层）
   - 理解用户意图
   - 提取任务关键信息
   - 判断任务复杂度
    ↓
2. Planner（规划层）
   - 任务智能分解
   - 生成执行步骤
   - 分配对应Agent
    ↓
3. Executor（执行层）
   ├─→ Researcher：网络搜索
   ├─→ Weather：天气查询
   ├─→ Writer：代码生成
   └─→ Sandbox：安全执行
    ↓
4. Critic（评审层）
   - 质量评估（0-1评分）
   - 结果验证
   - 反馈建议
    ↓
返回最终结果
```

### LangGraph 状态图

系统使用 LangGraph 管理复杂的 Agent 工作流：

```python
# 状态图节点
perceptor → planner → execute_plan → critic → finalize

# 执行节点可以循环，直到所有步骤完成
execute_plan ─┐
      ↑      │
      └──────┘ (继续下一步骤)
```

**关键设计点**：
- 🔁 **动态循环**: `execute_plan` 节点根据计划步骤数自动循环
- 🎯 **条件跳转**: 通过 `_should_continue_execution` 判断是否继续
- 📊 **状态累积**: 使用 `Annotated[List, operator.add]` 累积执行日志
- 🛡️ **错误处理**: 每个节点都有异常捕获和状态更新

### Agent 协作机制

```python
# 1. 数据流转
Researcher.search() 
    → 结果存入 prior_outputs["researcher"]
    → Writer.generate_code(research_data)

# 2. 上下文共享
class AgentContext:
    task_id: str          # 任务ID
    goal: str             # 任务目标
    payload: dict         # 步骤参数
    prior_outputs: dict   # 前序Agent输出

# 3. 智能路由
if "搜索" in goal:
    planner → Researcher → Writer
elif "天气" in goal:
    planner → Weather → Writer
else:
    planner → Writer
```

---

## 🏗️ 系统搭建逻辑

### 架构设计原则

#### 1. 分层解耦
```
L1 (UI Layer)
└─ Streamlit界面，只负责展示和用户交互

L2 (API Layer)  
└─ FastAPI网关，处理请求路由和任务调度

L3 (Agent Layer)
└─ 智能体执行，各Agent独立且可组合
```

#### 2. 依赖注入
```python
# app/orchestrator/factory.py
def build_orchestrator():
    # 统一创建所有依赖
    llm_proxy = LLMProxy()
    sandbox = Sandbox()
    storage = ObjectStorageClient()
    
    # 注入到各Agent
    writer = WriterAgent(llm_proxy, sandbox, storage)
    researcher = ResearcherAgent(search_tool, llm_proxy)
    
    # 构建编排器
    return LangGraphOrchestrator(
        writer=writer,
        researcher=researcher,
        ...
    )
```

#### 3. 状态持久化
```
Task Creation
    ↓
Database Record (PostgreSQL)
    ├─ task_id: 任务唯一标识
    ├─ status: pending/running/completed/failed
    ├─ result_summary: 执行结果
    └─ events[]: 事件日志
```

#### 4. 任务队列模式

**同步模式** (无Worker):
```
HTTP Request → 直接执行 → 返回结果
优点: 简单可靠
缺点: 请求会等待任务完成
```

**异步模式** (有Worker):
```
HTTP Request → 入队列 → 立即返回Task ID
           ↓
        Worker拉取 → 执行 → 更新状态
优点: 快速响应，可并发
缺点: 需要额外的Redis和Worker进程
```

### 核心模块构建

#### 1. LLM Proxy（统一LLM接口）
```python
class LLMProxy:
    def complete(self, request: LLMRequest) -> str:
        # 支持多个LLM提供商
        if provider == "openai": ...
        elif provider == "openrouter": ...
        else: return offline_fallback()
```

#### 2. Sandbox（安全代码执行）
```python
class Sandbox:
    def run_sync(self, code: str) -> SandboxResult:
        # 隔离子进程执行
        # 超时控制
        # 输出捕获
```

#### 3. Agent Base（智能体基类）
```python
class Agent:
    def execute(self, context: AgentContext) -> AgentResponse:
        # 统一的执行接口
        # 返回标准化响应
```

#### 4. Orchestrator（任务编排器）
```python
class LangGraphOrchestrator:
    def __init__(self, agents...):
        self.graph = self._build_graph()  # 构建状态图
        self.app = self.graph.compile()   # 编译为可执行应用
    
    def start_task(self, goal: str, sync: bool):
        # 创建初始状态
        # 调用 self.app.invoke()
        # 更新数据库
```

### 扩展新Agent的步骤

1. **创建Agent类**
```python
# app/agents/my_agent.py
class MyAgent(Agent):
    def execute(self, context: AgentContext) -> AgentResponse:
        # 实现你的逻辑
        return AgentResponse(success=True, output={...})
```

2. **注册到Factory**
```python
# app/orchestrator/factory.py
my_agent = MyAgent(llm_proxy)
orchestrator = LangGraphOrchestrator(..., my_agent=my_agent)
```

3. **添加到Planner识别**
```python
# app/agents/planner.py
if "my_keyword" in goal:
    steps.append({"agent": "MyAgent", ...})
```

---

## 🚀 快速开始

### 前置要求

**Docker方式（推荐）：**
- Docker 20.10+
- Docker Compose 2.0+

**本地方式：**
- Python 3.10+
- PostgreSQL 14+ (可选，已启用 pgvector)
- Redis 6+ (可选，用于异步任务)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/Lewis121025/Lewis-AI-System-.git
cd Lewis-AI-System-
```

2. **创建虚拟环境**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**

创建 `.env` 文件：
```bash
# API配置
API_TOKEN=change-me

# 数据库 (可选，默认使用 SQLite)
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/lewis

# Redis (可选)
REDIS_URL=redis://localhost:6379/0

# LLM API Keys
OPENROUTER_API_KEY=your_key_here
GOOGLE_SEARCH_API_KEY=your_key_here
GOOGLE_SEARCH_ENGINE_ID=your_id_here
WEATHER_API_KEY=your_key_here
```

### 启动服务

#### 方式1: Docker Compose（推荐）🐳

**一键启动所有服务：**
```bash
# 创建 .env 文件（可选，使用环境变量）
cat > .env << EOF
API_TOKEN=your-secure-token
OPENROUTER_API_KEY=your-key
GOOGLE_SEARCH_API_KEY=your-key
GOOGLE_SEARCH_ENGINE_ID=your-id
WEATHER_API_KEY=your-key
EOF

# 启动所有服务（PostgreSQL + Redis + Backend + Frontend + Worker）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

**服务地址：**
- 前端界面: http://localhost:8501
- API文档: http://localhost:8002/docs
- 健康检查: http://localhost:8002/health

**开发模式（热重载）：**
```bash
docker-compose -f docker-compose.dev.yml up
```

#### 方式2: 本地启动

**Windows 用户:**
```bash
# 1. 启动后端
start_backend.bat

# 2. 启动前端 (新窗口)
start_ui.bat

# 3. (可选) 启动Worker异步处理
start_worker.bat
```

**Linux/Mac 用户:**
```bash
# 1. 启动后端
uvicorn app.main:app --host 127.0.0.1 --port 8002

# 2. 启动前端 (新终端)
streamlit run ui/app.py

# 3. (可选) 启动Worker
python start_worker.py
```

### 访问系统

- **前端界面**: http://localhost:8501
- **API文档**: http://localhost:8002/docs
- **健康检查**: http://localhost:8002/health

---

## 🐳 Docker 部署

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/Lewis121025/Lewis-AI-System-.git
cd Lewis-AI-System-

# 使用Docker Compose一键启动
docker-compose up -d
```

### Docker Compose 服务

- **postgres**: PostgreSQL + pgvector 数据库
- **redis**: Redis 任务队列
- **backend**: FastAPI 后端服务
- **worker**: RQ Worker 异步任务处理
- **frontend**: Streamlit 前端界面

### 环境变量配置

创建 `.env` 文件或设置环境变量：

```bash
API_TOKEN=your-secure-token
OPENROUTER_API_KEY=your-openrouter-key
GOOGLE_SEARCH_API_KEY=your-google-search-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
WEATHER_API_KEY=your-weather-api-key
```

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重新构建镜像
docker-compose build --no-cache
```

### 单独构建镜像

```bash
# 构建后端镜像
docker build -t lewis-backend:latest .

# 构建前端镜像
docker build -f Dockerfile.frontend -t lewis-frontend:latest .

# 运行容器
docker run -d -p 8002:8002 --env-file .env lewis-backend:latest
```

---

## 📁 项目结构

```
Lewis-AI-System-/
├── app/
│   ├── agents/              # 智能体实现
│   │   ├── base.py         # Agent基类
│   │   ├── perceptor.py    # 感知智能体
│   │   ├── planner.py      # 规划智能体
│   │   ├── researcher.py   # 搜索智能体
│   │   ├── weather_agent.py # 天气智能体
│   │   ├── writer.py       # 写作智能体
│   │   ├── critic.py       # 评审智能体
│   │   └── llm_proxy.py    # LLM统一接口
│   ├── api/                 # FastAPI路由
│   ├── infrastructure/      # 基础设施
│   │   ├── db.py           # 数据库
│   │   ├── redis_queue.py  # 任务队列
│   │   └── telemetry.py    # 监控追踪
│   ├── models/              # 数据模型
│   ├── orchestrator/        # LangGraph编排器
│   └── main.py             # FastAPI应用
├── ui/
│   └── app.py              # Streamlit前端
├── tests/                   # 测试用例
├── screenshots/             # 界面截图
├── Dockerfile               # 后端Docker镜像
├── Dockerfile.frontend      # 前端Docker镜像
├── docker-compose.yml      # Docker Compose配置
├── docker-compose.dev.yml  # 开发环境配置
├── .dockerignore           # Docker忽略文件
├── start_backend.bat       # Windows启动脚本
├── start_ui.bat
├── start_worker.bat
└── requirements.txt         # 依赖列表
```

---

## 🎯 使用示例

### API调用示例

```python
import requests

API_BASE = "http://localhost:8002"
headers = {"Authorization": "Bearer change-me"}

# 创建任务
response = requests.post(
    f"{API_BASE}/tasks",
    json={
        "goal": "分析transformer架构的缺陷，输出markdown报告",
        "name": "Transformer架构分析",
        "sync": True
    },
    headers=headers
)

result = response.json()
print(f"Task ID: {result['task_id']}")
print(f"Status: {result['status']}")
```

### 支持的任务类型

✅ **搜索任务**: "搜索量子计算最新进展"  
✅ **天气查询**: "查询杭州近日天气，分析是否需要带伞"  
✅ **数据分析**: "对比分析日韩GDP，输出300字报告"  
✅ **代码生成**: "编写Python爬虫抓取新闻标题"  
✅ **报告撰写**: "分析transformer架构缺陷，预测改进方向"

---

## ⚙️ 配置说明

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `API_TOKEN` | API访问令牌 | `change-me` |
| `DATABASE_URL` | 数据库连接 | PostgreSQL |
| `REDIS_URL` | Redis地址 | `redis://localhost:6379/0` |
| `OPENROUTER_API_KEY` | LLM API密钥 | - |
| `GOOGLE_SEARCH_API_KEY` | 搜索API | - |
| `WEATHER_API_KEY` | 天气API | - |

### LangGraph 配置

系统默认递归限制为 **100**，适合处理复杂任务。如需调整：

```python
# app/orchestrator/langgraph_orchestrator.py
final_state = self.app.invoke(
    initial_state,
    config={"recursion_limit": 100}  # 可调整
)
```

---

## 🔍 智能体工作流

```mermaid
graph LR
    A[用户输入任务] --> B[Perceptor 感知]
    B --> C[Planner 规划]
    C --> D{任务类型}
    D -->|搜索| E[Researcher]
    D -->|天气| F[Weather]
    D -->|代码| G[Writer]
    E --> G
    F --> G
    G --> H[Sandbox 执行]
    H --> I[Critic 评审]
    I --> J[返回结果]
```

---

## 🐛 常见问题

### Q: Worker启动失败？
**A**: Worker不是必需的，系统会自动使用同步模式。如需异步，确保Redis正在运行。

### Q: 任务递归限制错误？
**A**: 已将限制提升至100。如仍不够，修改 `langgraph_orchestrator.py` 中的 `recursion_limit` 参数。

### Q: 端口8002被占用？
**A**: 说明后端已在运行。检查：`netstat -ano | findstr :8002`

---

## 📊 系统要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 硬盘: 2GB

### 推荐配置
- CPU: 4核+
- 内存: 8GB+
- 硬盘: 10GB+
- GPU: 可选（加速本地LLM）

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 更新日志

### v2.0 (2025-11)
- ✨ 新增 Researcher Agent 支持网络搜索
- ✨ 新增 Weather Agent 支持天气查询
- 🔧 修复 Writer Agent 编码问题
- 🔧 优化 LangGraph 递归限制
- 🎨 美化 Streamlit UI 界面
- 📝 完善文档和示例

### v1.0 (2025-10)
- 🎉 初始版本发布
- 🤖 实现基础智能体系统
- 🏗️ 搭建三层架构


---


## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态图编排
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Streamlit](https://streamlit.io/) - 数据应用框架

---

## 📧 联系方式

- GitHub: [@Lewis121025](https://github.com/Lewis121025)
- 项目地址: [Lewis Trinity AI Platform](https://github.com/Lewis121025/Lewis-AI-System-)

---

<div align="center">

**⭐ Peace and Love！**

Made with ❤️ by Lewis

</div>
