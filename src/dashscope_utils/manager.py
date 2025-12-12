import asyncio
import time
from typing import Optional

class RateLimitManager:
    def __init__(self, client, *, rps: Optional[float] = None, concurrency: Optional[int] = None):
        if (rps is None and concurrency is None) or (rps is not None and concurrency is not None):
            raise ValueError("必须在 rps 与 concurrency 中二选一")
        self.client = client
        self._rps = float(rps) if rps is not None else None
        self._concurrency = int(concurrency) if concurrency is not None else None

        self._rps_lock = asyncio.Lock()
        self._next_available = time.monotonic()
        self._semaphore = asyncio.Semaphore(self._concurrency) if self._concurrency else None

    async def chat(self, payload):
        if self._rps is not None:
            await self._acquire_rps()
            # 如果希望同时限制并发，可在这里再加 semaphore：
            if self._semaphore is not None:
                async with self._semaphore:
                    return await self.client.chat(payload)
            else:
                return await self.client.chat(payload)

        assert self._semaphore is not None
        async with self._semaphore:
            return await self.client.chat(payload)

    async def _acquire_rps(self) -> None:
        """
        1) 在锁内计算并更新下一次可用时间（schedule_time），然后释放锁。
        2) 在锁外 sleep 到 schedule_time（如果需要）。
        这样锁不在 sleep 的时候被占用，其他协程能快速进入排队阶段。
        """
        min_interval = 1.0 / self._rps  # type: ignore[operator]
        # 计算 schedule_time 并更新 next_available 原子地完成
        async with self._rps_lock:
            now = time.monotonic()
            schedule_time = max(self._next_available, now)
            self._next_available = schedule_time + min_interval

        # 在锁外等待到 schedule_time
        now = time.monotonic()
        wait = schedule_time - now
        if wait > 0:
            await asyncio.sleep(wait)
        # 然后返回，允许调用方开始 client.chat()


