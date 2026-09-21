# agent-engineering

从零手写 LLM Agent 的学习与实验仓库：不依赖任何框架，只用 Python 标准库把 Agent 的核心机制拆开看清楚。

## 内容

| 文件 | 说明 |
| --- | --- |
| `mini_agent.py` | 最迷你的 LLM Agent，约 100 行、零依赖。演示 Agent 主循环、function calling 工具调用与多步推理 |
| `.env.example` | 配置模板（`.env` 对应的可提交版本） |
| `src/agent_engineering/` | 项目包骨架（`uv` 管理） |

## mini_agent.py

只用 `json` + `urllib.request` 实现了完整闭环：

1. 把工具描述（OpenAI function-calling 格式）随消息一起发给模型；
2. 模型返回 `tool_calls` 时，本地执行对应函数，把结果以 `role: "tool"` 追加回消息历史；
3. 重复直到模型不再调用工具，返回最终答案（带 `max_steps` 上限防止死循环）。

内置一个示例工具 `get_weather`（假数据）。**所有配置都放在 `.env` 里，代码中不含任何密钥**：

```bash
cp .env.example .env     # 然后编辑 .env 填入你的 API_KEY
python3 mini_agent.py
```

`.env` 内容：

```ini
# 必须是完整的 chat/completions 端点，只写到 /v1 会 404
API_URL=https://api.deepseek.com/v1/chat/completions
API_KEY=sk-xxxxxxxx
MODEL=deepseek-flash
```

优先级：**真实环境变量 > `.env` > 代码内默认值**，所以在 CI / 服务器上直接 `export API_KEY=...` 也能覆盖。

> ⚠️ `.env` 已在 `.gitignore` 中，不会进仓库；只有模板 `.env.example` 会被提交。

运行：

## 环境

需要 Python 3.12+。项目使用 `uv` 管理：

```bash
uv sync
uv run agent-engineering
```

## License

未指定。
