"""
Auth middleware: validate JWT for protected paths; require admin for admin-only paths.
Sets request.state.user_id when token is valid.
- Protected paths (e.g. /api/users): 401 if no/invalid JWT.
- Admin-only paths (e.g. /api/auth/activation/generate): 401 if no/invalid JWT, 403 if not in ADMIN_USER_IDS.
- Other paths: optional decode sets user_id for rate limit.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.utils.security import decode_access_token

# Path prefixes that require a valid JWT.
PROTECTED_PREFIXES = ("/api/users", "/api/videos")
# Paths that require JWT + user_id in config ADMIN_USER_IDS (admin check in middleware, no DB).
ADMIN_REQUIRED_PREFIXES = ("/api/auth/activation/generate",)


def _is_protected_path(path: str) -> bool:
    return path.startswith(PROTECTED_PREFIXES)


def _is_admin_required_path(path: str) -> bool:
    return path.startswith(ADMIN_REQUIRED_PREFIXES)


def _get_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    return auth[7:].strip() or None


class AuthMiddleware(BaseHTTPMiddleware):
    """
    For protected paths: validate Bearer JWT; set request.state.user_id or return 401.
    For other paths: optionally decode and set user_id if token present (for uid-based rate limit).
    """

    async def dispatch(self, request: Request, call_next):
        path = request.scope.get("path", "")
        settings = get_settings()
        token = _get_bearer_token(request)
        user_id = None
        if token:
            payload = decode_access_token(token)
            if payload:
                raw = payload.get("user_id") or payload.get("sub")
                if raw is not None:
                    try:
                        user_id = int(raw)
                    except (ValueError, TypeError):
                        pass
        if user_id is None and getattr(settings, "TESTING", False):
            user_id = getattr(settings, "TESTING_USER_ID", 1)
        if user_id is not None:
            request.state.user_id = user_id
        if getattr(settings, "TESTING", False):
            pass  # skip auth enforcement
        elif _is_admin_required_path(path):
            if user_id is None:
                return JSONResponse(
                    status_code=401,
                    content={
                        "code": "TOKEN_MISSING_OR_INVALID",
                        "message": "Access token required or invalid. Try refreshing or log in again.",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )
            admin_ids = settings.admin_user_ids_list()
            if user_id not in admin_ids:
                return JSONResponse(
                    status_code=403,
                    content={
                        "code": "ADMIN_REQUIRED",
                        "message": "Admin access required.",
                    },
                )
        elif _is_protected_path(path) and user_id is None:
            return JSONResponse(
                status_code=401,
                content={
                    "code": "TOKEN_MISSING_OR_INVALID",
                    "message": "Access token required or invalid. Try refreshing or log in again.",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await call_next(request)
