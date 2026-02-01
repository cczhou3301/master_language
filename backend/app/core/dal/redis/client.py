"""
Redis client factory: one async client per DB index (cache, rate limit, session).
"""

from __future__ import annotations

import re

import redis.asyncio as aioredis

from app.config import get_settings

_settings = get_settings()
_clients: dict[int, aioredis.Redis] = {}


def _url_for_db(db: int) -> str:
    """Return Redis URL for the given DB index (0, 1, 2, ...)."""
    url = _settings.REDIS_URL.rstrip("/")
    # Replace trailing /N if present, else append /db
    if re.search(r"/\d+$", url):
        url = re.sub(r"/\d+$", f"/{db}", url)
    else:
        url = f"{url}/{db}"
    return url


async def get_client(db: int) -> aioredis.Redis:
    """Return shared async Redis client for the given DB. Lazy connect per DB."""
    if db not in _clients:
        _clients[db] = aioredis.from_url(
            _url_for_db(db),
            encoding="utf-8",
            decode_responses=True,
        )
    return _clients[db]


async def close_all() -> None:
    """Close all Redis connections (e.g. on app shutdown)."""
    for r in _clients.values():
        await r.aclose()
    _clients.clear()
