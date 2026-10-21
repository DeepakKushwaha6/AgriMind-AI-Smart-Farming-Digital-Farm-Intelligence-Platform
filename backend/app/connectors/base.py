import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
import httpx
from app.core.config import settings
from app.core.logging import logger


class BaseConnector(ABC):
    """Common base class for all external data connectors with circuit breaker and fallback."""

    def __init__(self, name: str, timeout: float = 10.0, max_retries: int = 3):
        self.name = name
        self.timeout = timeout
        self.max_retries = max_retries
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0

    def is_circuit_open(self) -> bool:
        return time.time() < self._circuit_open_until

    def record_success(self):
        self._consecutive_failures = 0
        self._circuit_open_until = 0.0

    def record_failure(self, error_message: str):
        self._consecutive_failures += 1
        logger.warning(f"[{self.name}] Failure #{self._consecutive_failures}: {error_message}")
        if self._consecutive_failures >= 3:
            # Trip circuit breaker for 60 seconds
            self._circuit_open_until = time.time() + 60.0
            logger.error(f"[{self.name}] Circuit tripped open for 60s due to consecutive failures")

    async def execute_with_retry(
        self,
        coro_func,
        *args,
        **kwargs
    ) -> Any:
        if self.is_circuit_open():
            raise RuntimeError(f"Circuit breaker open for connector {self.name}")

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await coro_func(*args, **kwargs)
                self.record_success()
                return result
            except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_error = exc
                if attempt == self.max_retries:
                    self.record_failure(str(exc))
                    raise exc
                # Exponential backoff with jitter
                sleep_sec = (1.5 ** attempt) + random.uniform(0.1, 0.5)
                await asyncio.sleep(sleep_sec)
        raise last_error
