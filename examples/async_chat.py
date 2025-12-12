import asyncio

from dashscope_utils import DashScopeClient, OpenAIClient, RateLimitManager


async def main() -> None:
    # 选择需要的客户端（任选一个）
    client = OpenAIClient(api_key="OPENAI_API_KEY", default_model="gpt-4o-mini")
    # client = DashScopeClient(api_key="DASHSCOPE_API_KEY", default_model="qwen-long")

    # rps 与 concurrency 二选一
    limiter = RateLimitManager(client, concurrency=5)
    # limiter = RateLimitManager(client, rps=10)

    payload = {
        "messages": [{"role": "user", "content": "请用一句话介绍下你自己"}],
        # 可以补充 temperature/top_p 等 SDK 原生参数
    }

    response = await limiter.chat(payload)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())

