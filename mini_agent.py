#!/usr/bin/env python3
"""最迷你的 LLM Agent —— 零依赖，仅用 Python 标准库。"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path


# ============ 配置加载 ============
def load_env_file(path: Path) -> None:
    """读取 .env（零依赖）。已存在的真实环境变量优先，不覆盖。"""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        # 去掉值与行尾注释之间的空白，并剥掉可选引号
        value = value.split(" #")[0].strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


load_env_file(Path(__file__).with_name(".env"))


# ============ 配置 ============
# 注意：API_URL 必须是「完整」的 chat completions 端点，
#       只写到 /v1 会返回 404 Not Found。
API_URL = os.environ.get(
    "API_URL", "https://api.deepseek.com/v1/chat/completions"
)
API_KEY = os.environ.get("API_KEY", "")  # 来自 .env 或环境变量，不写进代码
MODEL = os.environ.get("MODEL", "deepseek-flash")


# ============ 工具定义 ============
def get_weather(city: str) -> str:
    """一个示例工具：查天气（假数据）。"""
    fake = {"北京": "晴，25°C", "上海": "多云，22°C", "深圳": "雷阵雨，28°C"}
    return fake.get(city, f"{city}：暂无数据")


# 工具名 -> 函数 的映射
TOOLS = {"get_weather": get_weather}

# 给 LLM 看的工具描述（OpenAI function-calling 格式）
TOOLS_SCHEMA = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询某个城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "城市名"}},
            "required": ["city"],
        },
    },
}]


# ============ LLM 调用 ============
def call_llm(messages):
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["choices"][0]["message"]
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(
            f"LLM 请求失败 {e.code} {e.reason}\n"
            f"  URL: {API_URL}\n  响应: {detail[:500]}"
        ) from e


# ============ Agent 主循环 ============
def agent(user_input: str, max_steps: int = 10):
    messages = [
        {"role": "system", "content": "你是一个助手，需要时调用工具来回答。"},
        {"role": "user", "content": user_input},
    ]

    for _ in range(max_steps):
        msg = call_llm(messages)
        messages.append(msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:                       # 没有工具调用 => 最终答案
            return msg.get("content", "")

        for tc in tool_calls:                    # 执行每个工具调用
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            result = TOOLS[name](**args) if name in TOOLS else f"未知工具: {name}"
            print(f"  [tool] {name}({args}) -> {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": str(result),
            })

    return "（达到最大步数，未能完成）"


# ============ 运行 ============
if __name__ == "__main__":
    if not API_KEY:
        raise SystemExit(
            "未配置 API_KEY。请执行：\n"
            "  cp .env.example .env   然后把 API_KEY 填进去\n"
            "或直接 export API_KEY=sk-xxxxxx"
        )
    while True:
        try:
            q = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            continue
        print("Agent:", agent(q))
