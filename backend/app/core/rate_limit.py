"""
Rate limiting: IP and UID based. Redis-backed. Implements PRD §6.2.
"""

from __future__ import annotations

import time
from typing import Callable

import redis.asyncio as aioredis
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings

_settings = get_settings()
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            _settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


class RateLimiter:
    """Parse "N/seconds" and check against Redis sliding window."""

    def __init__(
        self,
        key_prefix: str,
        limit_rule: str,
        block_duration_seconds: int = 0,
        scope: str = "ip",
    ):
        # e.g. "5/600" -> 5 requests per 600 seconds
        parts = limit_rule.split("/")
        self.limit = int(parts[0]) if parts else 5
        self.window = int(parts[1]) if len(parts) > 1 else 60
        self.key_prefix = key_prefix
        self.block_duration = block_duration_seconds
        self.scope = scope  # "ip" | "uid"

    def _key(self, request: Request) -> str:
        ident = request.client.host if self.scope == "ip" else "anon"
        if (
            self.scope == "uid"
            and hasattr(request.state, "user_id")
            and request.state.user_id
        ):
            ident = str(request.state.user_id)
        return f"rl:{self.key_prefix}:{self.scope}:{ident}"

    def _block_key(self, request: Request) -> str:
        ident = request.client.host if self.scope == "ip" else "anon"
        if (
            self.scope == "uid"
            and hasattr(request.state, "user_id")
            and request.state.user_id
        ):
            ident = str(request.state.user_id)
        return f"rl:block:{self.key_prefix}:{self.scope}:{ident}"

    async def is_blocked(self, request: Request) -> bool:
        if self.block_duration <= 0:
            return False
        r = await get_redis()
        v = await r.get(self._block_key(request))
        return v is not None

    async def check(self, request: Request) -> None:
        """Raises HTTP 429 if over limit. Sets block if configured."""
        r = await get_redis()
        key = self._key(request)
        block_key = self._block_key(request)

        if await self.is_blocked(request):
            ttl = await r.ttl(block_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_BLOCKED",
                    "message": "System has detected unusual traffic. Please try again in {} minutes.".format(
                        max(1, (ttl + 59) // 60)
                    ),
                    "retry_after_seconds": ttl,
                },
            )

        now = time.time()
        window_start = now - self.window
        pipe = r.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, self.window + 60)
        _, _, count, _ = await pipe.execute()

        if count > self.limit:
            if self.block_duration > 0:
                await r.setex(block_key, self.block_duration, "1")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "You're tapping too fast. Please wait a moment.",
                    "retry_after_seconds": self.window,
                },
            )


def rate_limit_dependency(
    key_prefix: str,
    limit_rule: str,
    block_seconds: int = 0,
    scope: str = "ip",
) -> Callable:
    limiter = RateLimiter(key_prefix, limit_rule, block_seconds, scope)

    async def _(request: Request) -> None:
        await limiter.check(request)

    return _


# Predefined limiters from PRD §6.2
async def rate_limit_activation(request: Request) -> None:
    await RateLimiter(
        "activation",
        _settings.RATE_ACTIVATION_PER_IP,
        block_duration_seconds=_settings.ACTIVATION_BLOCK_IP_MINUTES * 60,
        scope="ip",
    ).check(request)


async def rate_limit_login(request: Request) -> None:
    # IP: 5/1min -> 15 min lock
    await RateLimiter(
        "login_ip",
        _settings.RATE_LOGIN_FAILED_PER_IP,
        block_duration_seconds=_settings.LOGIN_FAILED_LOCK_MINUTES * 60,
        scope="ip",
    ).check(request)


async def rate_limit_video_uid(request: Request) -> None:
    await RateLimiter(
        "video_uid",
        _settings.RATE_VIDEO_PER_UID,
        block_duration_seconds=0,  # throttle only, no block
        scope="uid",
    ).check(request)


async def rate_limit_video_ip(request: Request) -> None:
    await RateLimiter(
        "video_ip",
        _settings.RATE_VIDEO_PER_IP,
        block_duration_seconds=_settings.VIDEO_SCRAPE_BLOCK_IP_HOURS * 3600,
        scope="ip",
    ).check(request)


async def rate_limit_general_uid(request: Request) -> None:
    await RateLimiter(
        "general_uid",
        _settings.RATE_GENERAL_UID,
        block_duration_seconds=300,  # 5 min cooldown
        scope="uid",
    ).check(request)
