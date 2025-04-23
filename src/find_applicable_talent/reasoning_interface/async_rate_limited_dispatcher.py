import asyncio
import inspect
from typing import Callable, Any
from find_applicable_talent.util.logger import get_logger

logger = get_logger(__name__)

class AsyncRateLimitedTaskDispatcher:
    def __init__(self, capacity: int, refill_interval: float):
        """
        Rate-limited dispatcher that supports both sync and async tasks.
        :param capacity: Max number of calls allowed per time window.
        :param refill_interval: Time (in seconds) between token refills (e.g., 60 / 50 = 1.2s).
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_interval = refill_interval
        self.token_lock = asyncio.Lock()
        self.token_semaphore = asyncio.Semaphore(capacity)

        self._started = False
        self._start_lock = asyncio.Lock()
        self._refill_task = None

        logger.info(f"Async dispatcher created with {capacity} calls per {refill_interval * capacity:.1f} seconds.")

    async def ensure_started(self):
        """
        Start the refill loop once the event loop is available.
        """
        async with self._start_lock:
            if not self._started:
                self._refill_task = asyncio.create_task(self._refill_loop())
                self._started = True
                logger.info("Async dispatcher refill loop started.")

    async def _refill_loop(self):
        while True:
            async with self.token_lock:
                if self.tokens < self.capacity:
                    self.tokens += 1
                    self.token_semaphore.release()
            await asyncio.sleep(self.refill_interval)

    async def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Submit a function (sync or async) for execution under rate limit.
        :param fn: The function or coroutine to run.
        :return: The result of the task.
        """
        await self.ensure_started()
        await self.token_semaphore.acquire()
        async with self.token_lock:
            self.tokens -= 1

        try:
            result = fn(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            logger.error(f"Error in async dispatcher task: {e}")
            raise
