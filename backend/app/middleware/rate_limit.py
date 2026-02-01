"""
Rate limiting: IP and UID based, Redis-backed. Implements PRD §6.2.
Includes RateLimiter, predefined limiters, rate_limit_dependency, and RateLimitMiddleware
(per-path rate limit applied to each API request).
"""

from __future__ import annotations

import time
from typing import Callable

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import get_settings
from app.core.dal.redis import get_redis_rate_limit

_settings = get_settings()


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
        ident = (getattr(request.client, "host", None) or "anon") if self.scope == "ip" else "anon"
        if (
            self.scope == "uid"
            and hasattr(request.state, "user_id")
            and request.state.user_id
        ):
            ident = str(request.state.user_id)
        return f"rl:{self.key_prefix}:{self.scope}:{ident}"

    def _block_key(self, request: Request) -> str:
        ident = (getattr(request.client, "host", None) or "anon") if self.scope == "ip" else "anon"
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
        r = await get_redis_rate_limit()
        v = await r.get(self._block_key(request))
        return v is not None

    async def check(self, request: Request) -> None:
        """Raises HTTP 429 if over limit. Sets block if configured."""
        r = await get_redis_rate_limit()
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
        block_duration_seconds=0,
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
        block_duration_seconds=300,
        scope="uid",
    ).check(request)


# ---- Per-path rate limit middleware ----

def _get_limiter_for_path(path: str) -> RateLimiter | None:
    """Return the RateLimiter for this path, or None to skip (e.g. health, docs)."""
    # All /api/* endpoints: 5 requests per second per IP (configurable via RATE_API_PER_SECOND)
    if path.startswith("/api/"):
        return RateLimiter(
            "api_per_sec",
            _settings.RATE_API_PER_SECOND,
            block_duration_seconds=0,
            scope="ip",
        )
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply path-based rate limit before each request. Returns 429 if over limit."""

    async def dispatch(self, request: Request, call_next):
        path = request.scope.get("path", "")
        limiter = _get_limiter_for_path(path)
        if limiter is None:
            return await call_next(request)
        try:
            await limiter.check(request)
        except HTTPException as e:
            if e.status_code == 429:
                detail = e.detail if isinstance(e.detail, dict) else {"message": str(e.detail)}
                return JSONResponse(status_code=429, content=detail)
            raise
        return await call_next(request)
