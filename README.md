﻿# Lewis AI System - 三层自治智能系统

<div align="center">

**🤖 基于 LangGraph 的多智能体协作系统**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

</div>

---

## 📖 项目简介

Lewis AI System 是一个**三层架构**的自治智能系统，通过多个专业智能体（Agents）协作完成复杂任务。系统支持智能搜索、天气查询、代码生成、报告撰写等多种任务类型。

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

## 🚀 快速开始

### 前置要求

- Python 3.10+
- PostgreSQL 14+ (可选，已启用 pgvector)
- Redis 6+ (可选，用于异步任务)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/Lewis121025/Lewis-first-project.git
cd Lewis-first-project
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

**Windows 用户（推荐）:**
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

## 📁 项目结构

```
Lewis-first-project/
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

### v1.0 (2024)
- 🎉 初始版本发布
- 🤖 实现基础智能体系统
- 🏗️ 搭建三层架构

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态图编排
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Streamlit](https://streamlit.io/) - 数据应用框架

---

## 📧 联系方式

- GitHub: [@Lewis121025](https://github.com/Lewis121025)
- 项目地址: [Lewis-first-project](https://github.com/Lewis121025/Lewis-first-project)

---

<div align="center">

**⭐ Peace and Love！**

Made with ❤️ by Lewis

</div>