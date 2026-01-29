"""
Auth: Activation (invite-only), Login, 3-Device limit. Rate limiting per PRD §6.2.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import rate_limit_activation, rate_limit_login
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models import User, ActivationCode, UserDevice
from app.models.user import ActivationCodeStatus
from app.schemas.auth import (
    ActivationStep1,
    ActivationStep2,
    LoginRequest,
    LoginResponse,
    DeviceInfo,
    DeviceLimitError,
)

router = APIRouter(prefix="/auth", tags=["auth"])
_settings = get_settings()


# ---- Activation ----
@router.post("/activation/validate", dependencies=[Depends(rate_limit_activation)])
async def validate_activation_code(
    body: ActivationStep1,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Step 1: Check if code is valid and unused. PRD 1.1."""
    r = await db.execute(
        select(ActivationCode)
        .where(ActivationCode.code == body.code.strip())
        .where(ActivationCode.not_deleted())
    )
    row = r.scalar_one_or_none()
    if not row:
        raise HTTPException(
            status_code=400, detail={"code": "INVALID_CODE", "message": "Invalid Code"}
        )
    if row.status == ActivationCodeStatus.USED.value:
        raise HTTPException(
            status_code=400,
            detail={"code": "CODE_ALREADY_USED", "message": "Code already used."},
        )
    return {"valid": True, "code": body.code}


@router.post("/activation/register", dependencies=[Depends(rate_limit_activation)])
async def register_with_activation(
    body: ActivationStep2,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Step 2: Create account, burn code. PRD 1.1."""
    r = await db.execute(
        select(ActivationCode)
        .where(ActivationCode.code == body.code.strip())
        .where(ActivationCode.not_deleted())
    )
    ac = r.scalar_one_or_none()
    if not ac or ac.status == ActivationCodeStatus.USED.value:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_OR_USED",
                "message": "Invalid or already used code.",
            },
        )

    phone = body.phone.strip() if body.phone else None
    email = body.email.strip() if body.email else None
    if not phone and not email:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "PHONE_OR_EMAIL_REQUIRED",
                "message": "At least one of phone or email is required.",
            },
        )
    if phone:
        r = await db.execute(
            select(User).where(User.phone == phone).where(User.not_deleted())
        )
        if r.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail={"code": "PHONE_EXISTS", "message": "Phone already registered."},
            )
    if email:
        r = await db.execute(
            select(User).where(User.email == email).where(User.not_deleted())
        )
        if r.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail={"code": "EMAIL_EXISTS", "message": "Email already registered."},
            )

    user = User(
        phone=phone,
        email=email,
        password_hash=get_password_hash(body.password),
    )
    db.add(user)
    await db.flush()
    ac.status = ActivationCodeStatus.USED.value
    ac.used_by_user_id = user.id
    await db.refresh(user)
    token = create_access_token(str(user.id))
    return LoginResponse(
        access_token=token,
        user_id=user.id,
        phone=user.phone,
        email=user.email,
        level=user.level,
    )


# ---- Login with 3-Device limit ----
@router.post("/login", dependencies=[Depends(rate_limit_login)])
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """Login by phone or email. Hard block when 4th device. PRD 1.2, 1.3."""
    login_val = body.login.strip()
    r = await db.execute(
        select(User)
        .where(User.not_deleted())
        .where((User.phone == login_val) | (User.email == login_val))
    )
    user = r.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
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

    # Resolve current devices: same device_id gets refreshed
    r = await db.execute(
        select(UserDevice)
        .where(UserDevice.user_id == user.id)
        .where(UserDevice.not_deleted())
    )
    devices = list(r.scalars().all())

    # If this device_id exists, we're reconnecting: update and allow
    for d in devices:
        if d.device_id == body.device_id:
            d.device_name = body.device_name or d.device_name
            d.last_active_at = __utc_iso()
            token = create_access_token(str(user.id))
            return LoginResponse(
                access_token=token,
                user_id=user.id,
                phone=user.phone,
                email=user.email,
                level=user.level,
            )

    # New device: check 3-device limit
    if len(devices) >= _settings.MAX_DEVICES_PER_USER:
        active = [
            DeviceInfo(
                device_id=d.device_id,
                device_name=d.device_name or "Unknown",
                last_active=d.last_active_at or None,
            )
            for d in devices
        ]
        raise HTTPException(
            status_code=403,
            detail=DeviceLimitError(active_devices=active).model_dump(),
        )

    # Add new device
    dev = UserDevice(
        user_id=user.id,
        device_id=body.device_id,
        device_name=body.device_name or "Unknown",
        last_active_at=__utc_iso(),
    )
    db.add(dev)
    token = create_access_token(str(user.id))
    return LoginResponse(
        access_token=token,
        user_id=user.id,
        phone=user.phone,
        email=user.email,
        level=user.level,
    )


def __utc_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
