"""
Security: JWT (access + refresh), password hashing.
Access token: short-lived (15 min), stateless, validated by middleware.
Refresh token: long-lived (7 days), stateful in Redis, used only for /refresh.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

_settings = get_settings()

# bcrypt accepts at most 72 bytes; we pre-hash (salt+plain) with SHA-256 so long passwords work
BCRYPT_MAX_BYTES = 72


def _to_bcrypt_input(raw: bytes) -> bytes:
    """Ensure input to bcrypt is at most 72 bytes (pre-hash with SHA-256 if longer)."""
    if len(raw) <= BCRYPT_MAX_BYTES:
        return raw
    return hashlib.sha256(raw).digest()


def get_password_hash(plain: str, salt: str) -> str:
    """Hash (salt + password) with bcrypt. Salt is 32 bytes (e.g. secrets.token_hex(16)). Long inputs are pre-hashed to avoid bcrypt 72-byte limit."""
    raw = (salt + plain).encode("utf-8")
    payload = _to_bcrypt_input(raw)
    return bcrypt.hashpw(payload, bcrypt.gensalt()).decode("ascii")


def verify_password(plain: str, salt: str | None, hashed: str) -> bool:
    """Verify plain password using user's salt and stored hash. salt=None for legacy (no salt) users."""
    if not hashed:
        return False
    s = salt if salt is not None else ""
    raw = (s + plain).encode("utf-8")
    payload = _to_bcrypt_input(raw)
    try:
        return bcrypt.checkpw(payload, hashed.encode("ascii"))
    except Exception:
        return False


def create_access_token(
    sub: str,
    *,
    user_id: int | None = None,
    email: str | None = None,
    extra: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Short-lived JWT (default 15 min). Used for every request; validated by middleware."""
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(minutes=_settings.JWT_ACCESS_EXPIRE_MINUTES)
    expire = now + delta
    payload = {"sub": str(sub), "exp": expire, "iat": now, "type": "access"}
    if user_id is not None:
        payload["user_id"] = str(user_id)
    if email is not None:
        payload["email"] = email
    if extra:
        payload.update(extra)
    return jwt.encode(
        payload, _settings.JWT_SECRET_KEY, algorithm=_settings.JWT_ALGORITHM
    )


def create_refresh_token_string() -> str:
    """Long-lived random string (stored in Redis). Used only to obtain new access tokens."""
    return secrets.token_urlsafe(32)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate access JWT. Returns None if invalid or expired (caller returns 401)."""
    try:
        payload = jwt.decode(
            token,
            _settings.JWT_SECRET_KEY,
            algorithms=[_settings.JWT_ALGORITHM],
        )
        if payload.get("type") == "access":
            return payload
        return None
    except JWTError:
        return None
