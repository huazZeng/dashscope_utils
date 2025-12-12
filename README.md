## dashscope-utils

异步 LLM 客户端封装，支持 OpenAI 与 DashScope，并提供简单的速率控制器。

### 安装（开发模式）

```bash
pip install -e .
```

### 用法示例

```python
import asyncio
from dashscope_utils import OpenAIClient, DashScopeClient, RateLimitManager


async def main():
    # 任选其一：OpenAI
    client = OpenAIClient(api_key="OPENAI_API_KEY", default_model="gpt-4o")
    # 或 DashScope
    # client = DashScopeClient(api_key="DASHSCOPE_API_KEY", default_model="qwen-long")

    limiter = RateLimitManager(client, rps=5)  # 或 concurrency=10

    payload = {
        "model": "gpt-4o-mini",  # 未提供则使用 default_model
        "messages": [{"role": "user", "content": "你好，帮我总结以下文字..."}],
        # 这里可以放原生的 SDK 参数，如 temperature/top_p 等
    }

    result = await limiter.chat(payload)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### 设计要点
- 仅异步接口：OpenAI 使用官方 AsyncOpenAI，DashScope 当前官方为同步，内部用线程包裹以提供异步体验。
- 不强制 schema：`chat` 接收原始 `dict`，你可以自由传入 SDK 支持的字段；如需转换可继承覆盖 `_prepare_payload`。
- 速率控制：`rps`（均匀发放许可）或 `concurrency`（并发信号量），二选一。

