"""
Redis: separate async clients for cache, rate limit, session.
Each uses its own DB index; connections are lazy and shared per DB.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from app.core.dal.redis.client import get_client, close_all
from app.config import get_settings

_settings = get_settings()

# DB indexes from config
CACHE_DB = 0  # default / cache
RATE_LIMIT_DB = _settings.REDIS_RATE_LIMIT_DB
SESSION_DB = _settings.REDIS_SESSION_DB


async def get_redis_cache() -> aioredis.Redis:
    """Redis client for application cache (DB 0)."""
    return await get_client(CACHE_DB)


async def get_redis_rate_limit() -> aioredis.Redis:
    """Redis client for rate limiting (REDIS_RATE_LIMIT_DB)."""
    return await get_client(RATE_LIMIT_DB)


async def get_redis_session() -> aioredis.Redis:
    """Redis client for session storage (REDIS_SESSION_DB)."""
    return await get_client(SESSION_DB)


async def get_redis() -> aioredis.Redis:
    """Alias for rate-limit Redis (backward compat: main/health use this)."""
    return await get_redis_rate_limit()


async def close_redis() -> None:
    """Close all Redis connections (e.g. on app shutdown)."""
    await close_all()
