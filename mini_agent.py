#!/usr/bin/env python3
"""最迷你的 LLM Agent —— 零依赖，仅用 Python 标准库。"""

import json
import urllib.request

# ============ 配置 ============
API_URL = "https://api.openai.com/v1/chat/completions"  # 改成你的 API 地址
API_KEY = "sk-xxxxxxxx"                                  # 改成你的 API Key
MODEL   = "gpt-4o-mini"                                  # 改成你的模型名


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
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["choices"][0]["message"]


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
    while True:
        try:
            q = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            continue
        print("Agent:", agent(q))