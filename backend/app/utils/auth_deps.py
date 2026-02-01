"""
Auth dependency: validate short-lived Access Token on every request.
Returns 401 if missing, invalid, or expired (frontend should call /refresh or re-login).
get_current_admin_user_id lives in app.core.dal.auth_deps (uses DB; avoids cycle).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.utils.security import decode_access_token

_security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> int:
    """
    Return user_id for protected routes. Uses request.state.user_id set by AuthMiddleware when present;
    otherwise validates Bearer token (fallback if middleware order differs). Raises 401 if missing/invalid.
    When TESTING=True, returns TESTING_USER_ID if no valid token (no 401).
    """
    settings = get_settings()
    # Prefer user_id set by AuthMiddleware (JWT already validated in middleware)
    if hasattr(request.state, "user_id") and request.state.user_id is not None:
        return request.state.user_id
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    if not token:
        if getattr(settings, "TESTING", False):
            user_id = getattr(settings, "TESTING_USER_ID", 1)
            request.state.user_id = user_id
            return user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_MISSING", "message": "Access token required."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    raw = payload.get("user_id") if payload else None
    if raw is None and payload:
        raw = payload.get("sub")
    if not payload or raw is None:
        if getattr(settings, "TESTING", False):
            user_id = getattr(settings, "TESTING_USER_ID", 1)
            request.state.user_id = user_id
            return user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "TOKEN_INVALID_OR_EXPIRED",
                "message": "Token invalid or expired. Try refreshing or log in again.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = int(raw)
    except (ValueError, TypeError):
        if getattr(settings, "TESTING", False):
            user_id = getattr(settings, "TESTING_USER_ID", 1)
            request.state.user_id = user_id
            return user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_INVALID", "message": "Invalid token."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    request.state.user_id = user_id
    return user_id
