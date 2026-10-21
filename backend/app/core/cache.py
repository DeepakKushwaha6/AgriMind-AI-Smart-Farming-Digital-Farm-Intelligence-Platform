import time
from typing import Any, Dict, Optional, Tuple


class TTLMemoryCache:
    """Thread-safe TTL memory cache for connector snapshots and identical query results."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self._store: Dict[str, Tuple[float, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        expires_at, val = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        return val

    def get_with_age(self, key: str) -> Tuple[Optional[Any], Optional[float], bool]:
        """Returns (value, age_seconds, is_stale)."""
        if key not in self._store:
            return None, None, True
        expires_at, val = self._store[key]
        now = time.time()
        age = now - (expires_at - self.default_ttl)
        is_stale = now > expires_at
        return val, max(0.0, age), is_stale

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._store[key] = (time.time() + ttl, value)

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        self._store.clear()


# Global caches
weather_cache = TTLMemoryCache(default_ttl_seconds=3600)   # 1 hour
market_cache = TTLMemoryCache(default_ttl_seconds=21600)   # 6 hours
geocode_cache = TTLMemoryCache(default_ttl_seconds=86400 * 30)  # 30 days
ai_cache = TTLMemoryCache(default_ttl_seconds=1800)        # 30 mins
scraper_cache = TTLMemoryCache(default_ttl_seconds=7200)   # 2 hours
