"""
Auth service: activation validation/registration, login with device limit.
Uses repositories and core (security). API depends on this; no direct DB in API.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.const import ActivationCodeStatus
from app.core.dal.repository import (
    ActivationCodeRepository,
    UserRepository,
    UserDeviceRepository,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token_string,
)
from app.core.dal.redis.refresh_token_store import (
    save_refresh_token,
    get_user_id_by_refresh_token,
    get_user_id_and_device_id_by_refresh_token,
    revoke_refresh_token,
)
from app.dto import (
    LoginResponse,
    RefreshResponse,
    DeviceInfo,
    GenerateActivationCodesRequest,
    GenerateActivationCodesResponse,
)

_settings = get_settings()


def _utc_iso() -> str:
    """Current UTC time as ISO string (for last_active_at, etc.)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def register_with_activation(session: AsyncSession, body) -> LoginResponse:
    """Create account with activation code (validated here). Burn code and return access_token + refresh_token. PRD 1.1."""
    ac_repo = ActivationCodeRepository(session)
    user_repo = UserRepository(session)

    ac = await ac_repo.get_by_code(body.code.strip())
    if not ac or ac.status != ActivationCodeStatus.UNUSED:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_CODE",
                "message": "Invalid or already used activation code.",
            },
        )

    phone = (body.phone or "").strip() or None
    email = (body.email or "").strip() or None
    if not phone and not email:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "PHONE_AND_EMAIL_REQUIRED",
                "message": "Both phone and email are required.",
            },
        )
    if phone and (await user_repo.get_by_phone(phone)):
        raise HTTPException(
            status_code=400,
            detail={"code": "PHONE_EXISTS", "message": "Phone already registered."},
        )
    if email and (await user_repo.get_by_email(email)):
        raise HTTPException(
            status_code=400,
            detail={"code": "EMAIL_EXISTS", "message": "Email already registered."},
        )

    if len(body.password.encode("utf-8")) > 20:
        raise HTTPException(
            status_code=400,
            detail={"code": "PASSWORD_TOO_LONG", "message": "Password must be at most 20 bytes."},
        )

    password_salt = secrets.token_hex(16)  # 32 hex chars = 32 bytes
    password_hash = get_password_hash(body.password, password_salt)
    user = user_repo.create(
        phone=phone,
        email=email,
        password_salt=password_salt,
        password_hash=password_hash,
    )
    await user_repo.flush()
    await session.refresh(user)

    ac.status = ActivationCodeStatus.USED
    ac.used_by_user_id = user.id
    ac_repo.session.add(ac)
    await ac_repo.session.flush()

    access_token = create_access_token(
        str(user.id), user_id=user.id, email=user.email or ""
    )
    refresh_token = create_refresh_token_string()
    await save_refresh_token(refresh_token, user.id)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=_settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        user_id=user.id,
        phone=user.phone,
        email=user.email,
        level=user.level,
    )


async def login(session: AsyncSession, body) -> LoginResponse:
    """Login by phone or email. Hard block when 4th device. PRD 1.2, 1.3."""
    user_repo = UserRepository(session)
    device_repo = UserDeviceRepository(session)

    login_val = body.login.strip()
    if len(body.password.encode("utf-8")) > 20:
        raise HTTPException(
            status_code=400,
            detail={"code": "PASSWORD_TOO_LONG", "message": "Password must be at most 20 bytes."},
        )
    user = await user_repo.get_by_phone_or_email(login_val)
    if not user or not verify_password(
        body.password, user.password_salt, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid phone/email or password.",
            },
        )
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail={"code": "ACCOUNT_LOCKED", "message": "Account is locked."},
        )

    devices = await device_repo.list_by_user_id(user.id)
    active_only = [d for d in devices if d.status == "active"]

    for d in devices:
        if d.device_id == body.device_id:
            if d.status == "active":
                d.device_name = body.device_name or d.device_name
                d.last_active_at = _utc_iso()
                access_token = create_access_token(
                    str(user.id), user_id=user.id, email=user.email or ""
                )
                refresh_token = create_refresh_token_string()
                await save_refresh_token(refresh_token, user.id, body.device_id)
                return LoginResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=_settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
                    user_id=user.id,
                    phone=user.phone,
                    email=user.email,
                    level=user.level,
                )
            else:
                # logged_out: reactivate if under limit; no new record
                if len(active_only) >= _settings.MAX_DEVICES_PER_USER:
                    active = [
                        DeviceInfo(
                            device_id=x.device_id,
                            device_name=x.device_name or "Unknown",
                            last_active=x.last_active_at or None,
                        )
                        for x in active_only
                    ]
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "code": "DEVICE_LIMIT_REACHED",
                            "message": "Device limit reached. Please log out on another device.",
                            "active_devices": [a.model_dump() for a in active],
                        },
                    )
                d.status = "active"
                d.device_name = body.device_name or d.device_name
                d.last_active_at = _utc_iso()
                await device_repo.session.flush()
                access_token = create_access_token(
                    str(user.id), user_id=user.id, email=user.email or ""
                )
                refresh_token = create_refresh_token_string()
                await save_refresh_token(refresh_token, user.id, body.device_id)
                return LoginResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type="bearer",
                    expires_in=_settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
                    user_id=user.id,
                    phone=user.phone,
                    email=user.email,
                    level=user.level,
                )

    if len(active_only) >= _settings.MAX_DEVICES_PER_USER:
        active = [
            DeviceInfo(
                device_id=d.device_id,
                device_name=d.device_name or "Unknown",
                last_active=d.last_active_at or None,
            )
            for d in active_only
        ]
        raise HTTPException(
            status_code=403,
            detail={
                "code": "DEVICE_LIMIT_REACHED",
                "message": "Device limit reached. Please log out on another device.",
                "active_devices": [a.model_dump() for a in active],
            },
        )

    device_repo.add_device(
        user_id=user.id,
        device_id=body.device_id,
        device_name=body.device_name or "Unknown",
        last_active_at=_utc_iso(),
    )
    await device_repo.flush()

    access_token = create_access_token(
        str(user.id), user_id=user.id, email=user.email or ""
    )
    refresh_token = create_refresh_token_string()
    await save_refresh_token(refresh_token, user.id, body.device_id)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=_settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        user_id=user.id,
        phone=user.phone,
        email=user.email,
        level=user.level,
    )


async def refresh(session: AsyncSession, refresh_token: str) -> RefreshResponse:
    """Exchange valid refresh token for new access token. Returns 403 if token invalid/revoked."""
    user_id = await get_user_id_by_refresh_token(refresh_token)
    if user_id is None:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "LOGIN_REQUIRED",
                "message": "Refresh token invalid or expired. Please log in again.",
            },
        )
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "LOGIN_REQUIRED",
                "message": "User no longer exists. Please log in again.",
            },
        )
    access_token = create_access_token(
        str(user_id), user_id=user_id, email=user.email or ""
    )
    return RefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=_settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
    )


async def logout(session: AsyncSession, refresh_token: str) -> None:
    """Revoke refresh token and mark this device as logged_out. Idempotent."""
    user_id, device_id = await get_user_id_and_device_id_by_refresh_token(refresh_token)
    await revoke_refresh_token(refresh_token)
    if user_id is not None and device_id:
        device_repo = UserDeviceRepository(session)
        await device_repo.mark_logged_out(user_id, device_id)


def _generate_unique_code(prefix: str | None, existing: set[str]) -> str:
    """Generate a code of at most 32 chars. With prefix: prefix[:14]-<16 random>; else 16 random."""
    for _ in range(100):
        if prefix:
            p = (prefix.strip() or "")[:14]
            raw = secrets.token_urlsafe(12)
            code = f"{p}-{raw}" if p else raw
        else:
            code = secrets.token_urlsafe(16)
        if code not in existing and len(code) <= 32:
            existing.add(code)
            return code
    raise HTTPException(
        status_code=500,
        detail={
            "code": "CODE_GEN_FAILED",
            "message": "Could not generate unique codes.",
        },
    )


async def generate_activation_codes(
    session: AsyncSession, body: GenerateActivationCodesRequest
) -> GenerateActivationCodesResponse:
    """Admin: batch create unused activation codes. Returns list of codes (show once)."""
    ac_repo = ActivationCodeRepository(session)
    seen: set[str] = set()
    codes: list[str] = []
    for _ in range(body.count):
        code = _generate_unique_code(body.prefix, seen)
        ac_repo.create_code(code)
        codes.append(code)
    await ac_repo.session.flush()
    return GenerateActivationCodesResponse(codes=codes)
