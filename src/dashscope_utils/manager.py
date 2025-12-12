import asyncio
import time
from typing import Optional

from dashscope_utils.types import ChatPayload, ChatResult

from .clients.base import BaseLLMClient


class RateLimitManager:
     """
     rps：按秒稳定节流；concurrency：保持并发上限。
     仅允许二选一，保持简单可控。
     """

     def __init__(
         self,
         client: BaseLLMClient,
         *,
         rps: Optional[float] = None,
         concurrency: Optional[int] = None,
     ) -> None:
         if (rps is None and concurrency is None) or (rps is not None and concurrency is not None):
             raise ValueError("必须在 rps 与 concurrency 中二选一")

         self.client = client
         self._rps = float(rps) if rps is not None else None
         self._concurrency = int(concurrency) if concurrency is not None else None

         self._rps_lock = asyncio.Lock()
         self._next_available = time.monotonic()
         self._semaphore = asyncio.Semaphore(self._concurrency) if self._concurrency else None

     async def chat(self, payload: ChatPayload) -> ChatResult:
         if self._rps is not None:
             await self._acquire_rps()
             return await self.client.chat(payload)

         assert self._semaphore is not None  # for type checkers
         async with self._semaphore:
             return await self.client.chat(payload)

     async def _acquire_rps(self) -> None:
         min_interval = 1.0 / self._rps  # type: ignore[operator]
         async with self._rps_lock:
             now = time.monotonic()
             wait = max(0.0, self._next_available - now)
             if wait > 0:
                 await asyncio.sleep(wait)
             # 更新下一次可用时间，确保平均速率稳定
             now = time.monotonic()
             self._next_available = max(self._next_available, now) + min_interval

