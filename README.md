# DashScope Utils

基于 DashScope 官方 SDK 的异步客户端封装，支持多模态内容处理、文件上传、速率控制等功能。

## 主要特性

- **异步优先**: 基于 DashScope SDK ≥1.19.0 的原生异步接口
- **多模态支持**: 智能处理图像、视频内容，自动压缩和上传
- **思考模式**: 支持 `enable_thinking` 参数，获取 AI 推理过程
- **文件上传**: 自动处理大文件上传到临时 OSS 存储
- **速率控制**: 灵活的 RPS 或并发数限制
- **完整文档**: 详细的 API 使用指南和示例

## 安装

### 开发模式安装

```bash
pip install -e .
```

### 依赖要求

```bash
pip install dashscope>=1.19.0 requests pillow
```

## 快速开始

### 基本文本对话

```python
import asyncio
from dashscope_utils.clients import DashScopeClient

async def main():
    client = DashScopeClient(
        api_key="your-dashscope-api-key",
        default_model="qwen-plus",
        timeout=60
    )
    
    payload = {
        "messages": [
            {"role": "user", "content": "你好！请介绍一下自己。"}
        ]
    }
    
    response = await client.chat(payload)
    print(response)

asyncio.run(main())
```

### 多模态内容处理

```python
import asyncio
from dashscope_utils.clients import DashScopeClient

async def main():
    client = DashScopeClient(
        api_key="your-dashscope-api-key",
        default_model="qwen3-vl-plus"
    )
    
    payload = {
        "messages": [{
            "role": "user",
            "content": [
                {
                    "image": "https://example.com/image.jpg",
                    "max_pixels": 16384 * 32 * 32,
                    "min_pixels": 16384 * 4 * 4
                },
                {"text": "请描述这张图片的内容"}
            ]
        }],
        "enable_thinking": True,
        "thinking_budget": 10000
    }
    
    response = await client.chat(payload)
    print(response)

asyncio.run(main())
```

### 文件上传工具

```python
import asyncio
from dashscope_utils.utils import DashScopeFileUploader

async def main():
    uploader = DashScopeFileUploader(api_key="your-api-key")
    
    # 上传本地文件
    oss_url = uploader.upload_file("/path/to/large/video.mp4")
    print(f"上传成功: {oss_url}")
    
    # 获取详细信息
    result = uploader.upload_file_with_info("/path/to/image.jpg")
    print(f"文件: {result['file_name']}, 大小: {result['file_size']} bytes")
    print(f"OSS URL: {result['oss_url']}, 过期时间: {result['expire_time']}")

asyncio.run(main())
```

### 使用速率控制

```python
import asyncio
from dashscope_utils.clients import DashScopeClient
from dashscope_utils import RateLimitManager

async def main():
    client = DashScopeClient(
        api_key="your-dashscope-api-key",
        default_model="qwen-plus"
    )
    
    # 限制并发数为 5
    limiter = RateLimitManager(client, concurrency=5)
    
    # 批量请求
    payloads = [
        {"messages": [{"role": "user", "content": f"请告诉我数字 {i} 的趣事"}]}
        for i in range(10)
    ]
    
    # 并发执行，自动限流
    responses = await asyncio.gather(*[limiter.chat(p) for p in payloads])
    
    for i, response in enumerate(responses):
        print(f"响应 {i+1}: {response}")

asyncio.run(main())
```

## 支持的功能

### 多模态内容

| 类型 | 支持格式 | 自动处理 |
|------|----------|----------|
| **图像** | `file://`, `http://`, `https://`, `oss://` | >10MB 自动压缩 |
| **视频文件** | `file://`, `http://`, `https://`, `oss://` | >100MB 自动上传 OSS |
| **视频帧** | 图像URL列表 | 每帧自动压缩 |

### 思考模式参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `enable_thinking` | boolean | 开启思考过程 |
| `thinking_budget` | number | 最大推理 Token 数 |

### 图像分辨率控制

| 参数 | 类型 | 说明 |
|------|------|------|
| `max_pixels` | number | 最大分辨率 |
| `min_pixels` | number | 最小分辨率 |


### 视频抽帧参数（fps）

```python
messages = [
    {"role": "user",
     "content": [
        # fps 控制抽帧频率：每秒抽取 fps 帧（等价于每隔 1/fps 秒取一帧）
        {"video": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4", "fps": 2},
        {"text": "这段视频的内容是什么?"}
     ]}
]
```

- `fps`：可选，视频抽帧频率。不传则使用模型默认抽帧策略；更多含义参考官方文档（同阿里云 API 说明）。

## 完整文档

- [API 使用指南](src/dashscope_utils/clients/api.md) - 详细的参数说明和使用示例
- [示例代码](examples/) - 完整的测试和使用示例

## 核心设计

### 智能媒体处理
- **本地文件**: 自动检测文件大小，超过限制自动压缩或上传
- **网络资源**: 直接使用，无额外处理
- **OSS 资源**: 透传使用，保持高效

### 异步优先
- 使用 DashScope SDK ≥1.19.0 的原生异步接口 (`AioGeneration`, `AioMultiModalConversation`)
- 支持高并发请求处理
- 自动超时控制和错误处理

### 灵活扩展
- 不强制 schema，支持原生 SDK 参数
- 可继承 `BaseLLMClient` 自定义实现
- 模块化设计，工具函数可独立使用

## 使用场景

- **AI 应用开发**: 文本对话、图像理解、视频分析
- **多模态处理**: 自动处理各种媒体文件格式
- **批量处理**: 高并发请求与速率控制
- **文件上传**: 大文件自动上传到临时存储

## 环境变量

```bash
# 必需：DashScope API Key
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

Apache 2.0

