"""DTOs generated from IDL (auth_pb2). Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ActivationStep1(BaseModel):
    """Generated from idl message."""
    code: str = ""


class ActivationStep2(BaseModel):
    """Generated from idl message."""
    code: str = ""
    phone: str | None = None
    email: str | None = None
    password: str = ""


class LoginRequest(BaseModel):
    """Generated from idl message."""
    login: str = ""
    password: str = ""
    device_id: str = ""
    device_name: str = ""


class LoginResponse(BaseModel):
    """Generated from idl message."""
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"
    expires_in: int = 900  # seconds (15 min); frontend uses this to know when to refresh
    user_id: int = 0
    phone: str | None = None
    email: str | None = None
    level: str = ""


class RefreshRequest(BaseModel):
    """Optional body for /refresh; refresh_token can also be in HttpOnly cookie."""
    refresh_token: str | None = None


class RefreshResponse(BaseModel):
    """New access token after valid refresh."""
    access_token: str = ""
    token_type: str = "bearer"
    expires_in: int = 900


class LogoutRequest(BaseModel):
    """Optional body for /logout; refresh_token can also be in HttpOnly cookie."""
    refresh_token: str | None = None


class GenerateActivationCodesRequest(BaseModel):
    """Admin: batch generate activation codes."""
    count: int = Field(ge=1, le=100, description="Number of codes to generate (1–100)")
    prefix: str | None = Field(default=None, max_length=16, description="Optional prefix for each code (e.g. BATCH01)")


class GenerateActivationCodesResponse(BaseModel):
    """List of generated activation codes (show once; store securely)."""
    codes: list[str] = Field(default_factory=list)


class DeviceInfo(BaseModel):
    """Generated from idl message."""
    device_id: str = ""
    device_name: str = ""
    last_active: str | None = None


class DeviceLimitError(BaseModel):
    """Generated from idl message."""
    code: str = ""
    message: str = ""
    active_devices: list[DeviceInfo] = Field(default_factory=list)
