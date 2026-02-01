"""
Auth: Activation, Login (access + refresh tokens), Refresh, Logout.
Access token: short-lived (15 min), validated by dependency on every request.
Refresh token: long-lived (7 days), stored in Redis; used only for POST /refresh.
API calls service only; no direct DB or repository usage.
"""

from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dal import get_db
from app.core.router import auth_router
from app.dto import (
    ActivationStep2,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    LogoutRequest,
    GenerateActivationCodesRequest,
    GenerateActivationCodesResponse,
)
from app.service import auth_service

router = auth_router

# Cookie name for refresh token (frontend can set HttpOnly cookie; we accept body or cookie)
REFRESH_TOKEN_COOKIE = "refresh_token"


def _get_refresh_token(request: Request, body_token: str | None) -> str | None:
    """Prefer body, then cookie. Frontend should send in body or set HttpOnly cookie."""
    if body_token and body_token.strip():
        return body_token.strip()
    return request.cookies.get(REFRESH_TOKEN_COOKIE)


@auth_router.post("/activation/register")
async def register_with_activation(
    body: ActivationStep2,
    session: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Create account with activation code (validated inside). Returns access_token + refresh_token. PRD 1.1."""
    return await auth_service.register_with_activation(session, body)


@auth_router.post("/login")
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Login by phone or email. Returns access_token (15 min) + refresh_token (7 days). PRD 1.2, 1.3."""
    return await auth_service.login(session, body)


@auth_router.post("/refresh")
async def refresh(
    request: Request,
    body: RefreshRequest | None = None,
    session: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    """
    Exchange refresh token for new access token.
    Refresh token can be in body or in HttpOnly cookie (refresh_token).
    Returns 403 if token invalid/revoked → user must log in again.
    """
    token = _get_refresh_token(request, body.refresh_token if body else None)
    if not token:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail={
                "code": "LOGIN_REQUIRED",
                "message": "Refresh token required. Please log in again.",
            },
        )
    return await auth_service.refresh(session, token)


@auth_router.post("/logout")
async def logout(
    request: Request,
    body: LogoutRequest | None = None,
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke refresh token and mark this device as logged_out. Token can be in body or cookie."""
    token = _get_refresh_token(request, body.refresh_token if body else None)
    if token:
        await auth_service.logout(session, token)
    return {"message": "Logged out"}


@auth_router.post("/activation/generate")
async def generate_activation_codes(
    body: GenerateActivationCodesRequest,
    session: AsyncSession = Depends(get_db),
) -> GenerateActivationCodesResponse:
    """Admin only: batch generate activation codes (1–100). Show codes once; store securely."""
    return await auth_service.generate_activation_codes(session, body)
