

from termios import IXOFF
from typing import Any, Dict, Optional

from dashscope.aigc.generation import AioGeneration
from dashscope.aigc.multimodal_conversation import AioMultiModalConversation
from ..utils.media_utils import process_media_content

from .base import BaseLLMClient, ChatPayload, ChatResult


class DashScopeClient(BaseLLMClient):
    """
    基于 DashScope 官方 SDK 的适配任务实现。

    - 直接使用官方异步接口 AioGeneration / AioMultiModalConversation，兼容多模态。
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: float = 300,
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, default_model=default_model)
        self._api_key = api_key
        self._base_url = base_url
        self._default_model = default_model
        self._timeout = timeout

    def _prepare_payload(self, payload: ChatPayload) -> ChatPayload:
        messages = payload.get("messages", [])
        model_name = payload.get("model") or self._default_model or "qwen-vl-plus"
        
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                msg["content"] = process_media_content(content, self._api_key, model_name)
        
        return payload

    async def _execute_chat(self, prepared_payload: ChatPayload) -> ChatResult:
        
        model = prepared_payload.get("model") or self.default_model
        if not model:
            raise ValueError("model 未提供，也未设置 default_model")

        messages = prepared_payload.get("messages")

        # 是否使用多模态接口：自动检测 content 是否包含多模态字段
        use_multimodal = _contains_multimodal_content(messages)
        extra = {
            k: v
            for k, v in prepared_payload.items()
            if k not in {"model", "messages", "timeout"}
        }

        if use_multimodal:
            result = await AioMultiModalConversation.call(model=model,
                                                          messages=messages,
                                                          api_key=self._api_key,
                                                          timeout=self._timeout if prepared_payload.get("timeout") is None else prepared_payload.get("timeout"),
                                                          **extra)
        else:
            result = await AioGeneration.call(model=model, 
                                              messages=messages,
                                              api_key=self._api_key,
                                              timeout=self._timeout if prepared_payload.get("timeout") is None else prepared_payload.get("timeout"),
                                              **extra)
            
        
        if hasattr(result, "to_dict"):
            return result.to_dict()
        return result if isinstance(result, dict) else {"response": result}


def _contains_multimodal_content(messages: Any) -> bool:
    """简单检测 messages 是否包含多模态内容（如 image/audio/video）。"""
    if not isinstance(messages, list):
        return False
    for item in messages:
        content = item.get("content") if isinstance(item, dict) else None
        if isinstance(content, list):
            return True
        if isinstance(content, dict) and any(k in content for k in ("image", "audio", "video")):
            return True
    return False