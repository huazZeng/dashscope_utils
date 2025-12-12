# DashScope Utils API 文档

## 客户端使用指南

### DashScopeClient

基于 DashScope 官方 SDK 的异步客户端实现，支持文本、图像、视频等多模态内容。

#### 初始化

```python
from dashscope_utils.clients import DashScopeClient

client = DashScopeClient(
    api_key="your-api-key",              # 必需：DashScope API Key
    base_url="https://dashscope.aliyuncs.com/api/v1",  # 可选：API 基础地址
    default_model="qwen-plus",           # 可选：默认模型名称
    timeout=300                          # 可选：请求超时时间（秒），默认300秒
)
```

#### 消息格式

##### 基本消息结构
```python
payload = {
    "model": "qwen3-vl-plus",           # 模型名称（可选，使用default_model）
    "messages": [                        # 消息列表
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"}
    ],
    "timeout": 60,                      # 可选：覆盖默认超时时间
    "enable_thinking": True,            # 可选：开启思考过程
    "thinking_budget": 81920,           # 可选：最大推理过程 Token 数
    # 其他 DashScope API 参数...
}

result = await client.chat(payload)
```

##### 支持的角色类型
- `system`: 系统消息，用于设定助手行为
- `user`: 用户消息
- `assistant`: 助手回复消息

##### 消息内容格式

**文本消息**
```python
{"role": "user", "content": "请介绍一下人工智能"}
```

#### 多模态内容支持

##### 图像处理
```python
messages = [{
    "role": "user",
    "content": [
        {"image": "file:///local/path/image.png", 
         "max_pixels": 16384 * 32 * 32,    # 控制最大分辨率
         "min_pixels": 16384 * 4 * 4},     # 控制最小分辨率
        {"text": "图中描绘的是什么景象?"}
    ]
}]
```

##### 视频处理
```python
messages = [{
    "role": "user", 
    "content": [
        {"video": "file:///local/path/video.mp4", "fps": 2},
        {"text": "这段视频描绘的是什么景象?"}
    ]
}]
```

##### 支持的字段

**Payload 级别字段**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `enable_thinking` | boolean | 开启思考过程（qwen3-vl-plus、qwen3-vl-flash支持开启/关闭；qwen3-vl-235b-a22b-thinking等带thinking后缀模型仅支持开启） |
| `thinking_budget` | number | 最大推理过程 Token 数，默认 81920 |
| `timeout` | number | 请求超时时间（秒） |

**多模态内容字段**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `text` | string | 文本内容 |
| `image_url` | string | 图像路径或URL |
| `max_pixels` | number | 图像最大分辨率，如 16384 * 32 * 32 |
| `min_pixels` | number | 图像最小分辨率，如 16384 * 4 * 4 |
| `video_url` | string \| array | 视频文件路径或图像URL列表 |
| `fps` | number | 视频抽帧参数，控制抽帧频率 |

