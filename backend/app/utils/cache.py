"""
Lightweight in-memory TTL cache.

Deliberately simple for the initial deployment (no external dependency,
no extra infra to run locally). The interface is small enough that a
Redis-backed implementation could be swapped in later without touching
callers.
"""
from __future__ import annotations

import time
from typing import Any


class TTLCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self._store: dict[str, tuple[float, Any]] = {}
        self._default_ttl = default_ttl_seconds

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() >= expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._store[key] = (time.monotonic() + ttl, value)

    def age_seconds(self, key: str, ttl_seconds: int | None = None) -> float | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, _ = entry
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        return max(0.0, ttl - (expires_at - time.monotonic()))

    def clear(self) -> None:
        self._store.clear()


# Process-wide singleton. Fine for a single-instance deployment; swap for
# Redis (keyed the same way) if the app is scaled horizontally.
cache = TTLCache()


def cache_key(*parts: str) -> str:
    return ":".join(parts)
