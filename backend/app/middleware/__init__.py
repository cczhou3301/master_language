"""
Middleware: logging, auth, rate limiting.
Redis client is provided by app.core.dal.redis; re-exported here for convenience.
"""

from __future__ import annotations

from app.core.dal.redis import get_redis
from app.middleware.rate_limit import (
    RateLimiter,
    RateLimitMiddleware,
    rate_limit_dependency,
    rate_limit_activation,
    rate_limit_login,
    rate_limit_video_uid,
    rate_limit_video_ip,
    rate_limit_general_uid,
)

__all__ = [
    "get_redis",
    "RateLimiter",
    "RateLimitMiddleware",
    "rate_limit_dependency",
    "rate_limit_activation",
    "rate_limit_login",
    "rate_limit_video_uid",
    "rate_limit_video_ip",
    "rate_limit_general_uid",
]
