# LangGraph 迁移说明

项目已成功迁移到 LangGraph 框架。

## 安装依赖

如果遇到版本兼容性问题，请运行：

```bash
pip install --upgrade langchain langchain-core langgraph
```

或者：

```bash
pip install -r requirements.txt --upgrade
```

## 版本要求

- langchain >= 0.3.0
- langchain-core >= 0.3.0  
- langgraph >= 0.2.40

## 主要变更

1. **编排器迁移**：从 `TaskOrchestrator` 迁移到 `LangGraphOrchestrator`
2. **工作流定义**：使用 LangGraph 的 StateGraph 定义工作流
3. **状态管理**：使用 TypedDict 定义状态，支持类型安全
4. **API兼容性**：保持所有公共API接口不变

## 测试

运行测试脚本：

```bash
python test_four_tasks.py
```

确保后端服务已启动：

```bash
python start_backend.py
```

