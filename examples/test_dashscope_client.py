import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from dashscope_utils.clients import DashScopeClient


async def test_text_chat():
    """测试基本文本对话"""
    print("=" * 50)
    print("测试基本文本对话")
    print("=" * 50)
    
    client = DashScopeClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        default_model="qwen-plus",
        timeout=60
    )
    
    payload = {
        "messages": [
            {"role": "system", "content": "你是一个有用的AI助手。"},
            {"role": "user", "content": "请用一句话介绍你自己"}
        ],
        "temperature": 0.7
    }
    
    try:
        response = await client.chat(payload)
        print("请求成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"请求失败: {e}")
    print()


async def test_thinking_mode():
    """测试思考模式"""
    print("=" * 50)
    print("测试思考模式")
    print("=" * 50)
    
    client = DashScopeClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        default_model="qwen3-vl-plus",
        timeout=120
    )
    
    payload = {
        "messages": [
            {"role": "user", "content": "请解释一下量子计算的基本原理"}
        ],
    }
    
    try:
        response = await client.chat(payload)
        
        print("思考模式请求成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"思考模式请求失败: {e}")
    print()


async def test_multimodal_chat():
    """测试多模态对话（如果有本地文件的话）"""
    print("=" * 50)
    print("测试多模态对话")
    print("=" * 50)
    
    client = DashScopeClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        default_model="qwen3-vl-plus"
    )
    
    # 测试网络图片
    payload = {
        "messages": [{
            "role": "user",
            "content": [
                {
                    "image": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
                    "max_pixels": 16384 * 16 * 16,
                    "min_pixels": 16384 * 4 * 4
                },
                {"text": "请描述这张图片的内容"}
            ]
        }]
    }
    
    try:
        response = await client.chat(payload)
        print("多模态请求成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"多模态请求失败: {e}")
    print()


async def test_video_frames():
    """测试视频帧处理"""
    print("=" * 50)
    print("测试视频帧处理")
    print("=" * 50)
    
    client = DashScopeClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        default_model="qwen3-vl-plus"
    )
    
    # 测试视频帧列表
    payload = {
        "messages": [{
            "role": "user",
            "content": [
                {
                    "video": [
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/xzsgiz/football1.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/tdescd/football2.jpg",
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football3.jpg"
                        "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241108/zefdja/football4.jpg"
                    ],
                    "fps": 2
                },
                {"text": "请描述这个视频序列展示的内容"}
            ]
        }]
    }
    
    try:
        response = await client.chat(payload)
        print("视频帧请求成功！")
        print(f"响应: {response}")
    except Exception as e:
        print(f"视频帧请求失败: {e}")
    print()


async def test_concurrent_requests():
    """测试并发请求"""
    print("=" * 50)
    print("测试并发请求")
    print("=" * 50)
    
    client = DashScopeClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        default_model="qwen-plus"
    )
    
    # 创建多个不同的请求
    payloads = [
        {
            "messages": [{"role": "user", "content": f"请告诉我关于数字 {i} 的一个有趣事实"}]
        } for i in range(1, 4)
    ]
    
    try:
        # 并发执行
        responses = await asyncio.gather(*[client.chat(payload) for payload in payloads])
        print("并发请求成功！")
        for i, response in enumerate(responses):
            print(f"响应 {i+1}: {response}")
    except Exception as e:
        print(f"并发请求失败: {e}")
    print()


async def main():
    """主测试函数"""
    print("开始测试 DashScopeClient...")
    
    # 检查API Key
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    # 运行所有测试
    await test_text_chat()
    await test_thinking_mode()
    await test_multimodal_chat()
    await test_video_frames()
    await test_concurrent_requests()
    
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
