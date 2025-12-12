from abc import ABC, abstractmethod
from typing import Optional

from dashscope_utils.types import ChatPayload, ChatResult


class BaseLLMClient(ABC):
    """抽象客户端，留出 payload 预处理与发送的扩展点。"""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model

    async def chat(self, payload: ChatPayload) -> ChatResult:
        prepared = self._prepare_payload(payload)
        return await self._execute_chat(prepared)

    def _prepare_payload(self, payload: ChatPayload) -> ChatPayload:
        """
        子类可覆盖：用于调整/规范化传入的 payload。
        默认直接透传。
        """
        return payload

    @abstractmethod
    async def _execute_chat(self, prepared_payload: ChatPayload) -> ChatResult:
        """子类实现实际的调用逻辑。"""
        raise NotImplementedError
