"""
Refresh token storage in Redis (session DB). Stateful; allows revoke on logout.
Key: refresh_token:{token}, Value: user_id or user_id:device_id, TTL: JWT_REFRESH_EXPIRE_DAYS.
Storing device_id allows removing this device from user_device on logout.
"""

from __future__ import annotations

from app.config import get_settings
from app.core.dal.redis import get_redis_session

_settings = get_settings()
REFRESH_PREFIX = "refresh_token:"
TTL_SECONDS = _settings.JWT_REFRESH_EXPIRE_DAYS * 24 * 3600
_SEP = "\t"  # user_id and device_id separator (device_id may contain ":")


async def save_refresh_token(
    refresh_token: str, user_id: int, device_id: str | None = None
) -> None:
    """Store refresh token -> user_id (and device_id if provided) with TTL. Call after login."""
    r = await get_redis_session()
    key = f"{REFRESH_PREFIX}{refresh_token}"
    val = str(user_id)
    if device_id:
        val = f"{user_id}{_SEP}{device_id}"
    await r.setex(key, TTL_SECONDS, val)


async def get_user_id_by_refresh_token(refresh_token: str) -> int | None:
    """Return user_id if token is valid and not revoked; else None."""
    uid, _ = await get_user_id_and_device_id_by_refresh_token(refresh_token)
    return uid


async def get_user_id_and_device_id_by_refresh_token(
    refresh_token: str,
) -> tuple[int | None, str | None]:
    """Return (user_id, device_id) if token is valid; else (None, None). device_id may be None."""
    if not refresh_token:
        return None, None
    r = await get_redis_session()
    key = f"{REFRESH_PREFIX}{refresh_token}"
    val = await r.get(key)
    if val is None:
        return None, None
    parts = val.split(_SEP, 1)
    try:
        uid = int(parts[0])
        did = parts[1] if len(parts) > 1 and parts[1] else None
        return uid, did
    except ValueError:
        return None, None


async def revoke_refresh_token(refresh_token: str) -> None:
    """Revoke (delete) refresh token. Call on logout."""
    if not refresh_token:
        return
    r = await get_redis_session()
    key = f"{REFRESH_PREFIX}{refresh_token}"
    await r.delete(key)
