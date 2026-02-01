"""
DAL: data access layer. Re-export repository, Redis, and auth deps (admin check).
"""

from __future__ import annotations

from app.core.dal.repository import (
    get_db,
    engine,
    AsyncSessionLocal,
    init_db,
    BaseRepository,
    UserRepository,
    ActivationCodeRepository,
    UserDeviceRepository,
    VideoRepository,
    SubtitleLineRepository,
)
from app.core.dal.redis import (
    get_redis,
    get_redis_cache,
    get_redis_rate_limit,
    get_redis_session,
    close_redis,
)
from app.core.dal.repository import get_current_admin_user_id

__all__ = [
    "get_db",
    "engine",
    "AsyncSessionLocal",
    "init_db",
    "get_redis",
    "get_redis_cache",
    "get_redis_rate_limit",
    "get_redis_session",
    "close_redis",
    "BaseRepository",
    "UserRepository",
    "ActivationCodeRepository",
    "UserDeviceRepository",
    "VideoRepository",
    "SubtitleLineRepository",
    "get_current_admin_user_id",
]
