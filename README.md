# agent-engineering

从零手写 LLM Agent 的学习与实验仓库：不依赖任何框架，只用 Python 标准库把 Agent 的核心机制拆开看清楚。

## 内容

| 文件 | 说明 |
| --- | --- |
| `mini_agent.py` | 最迷你的 LLM Agent，约 100 行、零依赖。演示 Agent 主循环、function calling 工具调用与多步推理 |
| `src/agent_engineering/` | 项目包骨架（`uv` 管理） |

## mini_agent.py

只用 `json` + `urllib.request` 实现了完整闭环：

1. 把工具描述（OpenAI function-calling 格式）随消息一起发给模型；
2. 模型返回 `tool_calls` 时，本地执行对应函数，把结果以 `role: "tool"` 追加回消息历史；
3. 重复直到模型不再调用工具，返回最终答案（带 `max_steps` 上限防止死循环）。

内置一个示例工具 `get_weather`（假数据）。运行前请修改文件顶部的配置：

```python
API_URL = "https://api.openai.com/v1/chat/completions"  # 你的 API 地址（兼容 OpenAI 协议即可）
API_KEY = "sk-xxxxxxxx"                                  # 你的 API Key
MODEL   = "gpt-4o-mini"                                  # 模型名
```

> ⚠️ 不要把真实 API Key 提交到仓库——建议改成从环境变量读取。

运行：

```bash
python3 mini_agent.py
```

## 环境

需要 Python 3.12+。项目使用 `uv` 管理：

```bash
uv sync
uv run agent-engineering
```

## License

未指定。
