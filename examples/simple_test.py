import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from dashscope_utils.clients import DashScopeClient


async def main():
    """简单测试 DashScopeClient 的基本功能"""
    
    # 检查API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    print("🚀 开始测试 DashScopeClient...")
    
    # 创建客户端
    client = DashScopeClient(
        api_key=api_key,
        default_model="qwen-plus",
        timeout=30
    )
    
    # 简单的文本对话测试
    payload = {
        "messages": [
            {"role": "user", "content": "你好！请简单介绍一下自己。"}
        ]
    }
    
    try:
        print("📤 发送请求...")
        response = await client.chat(payload)
        
        print("✅ 请求成功！")
        print("📋 完整响应:")
        print(response)
        print()
        
        # 尝试提取消息内容
        if isinstance(response, dict):
            if "output" in response and "choices" in response["output"]:
                message_content = response["output"]["text"]
                print("💬 AI回复:")
                print(message_content)
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
