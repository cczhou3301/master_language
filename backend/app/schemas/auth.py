from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ActivationStep1(BaseModel):
    code: str = Field(..., min_length=4, max_length=32)


class ActivationStep2(BaseModel):
    code: str = Field(..., min_length=4, max_length=32)
    phone: str | None = Field(default=None, min_length=1, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    password: str = Field(..., min_length=6, max_length=128)

    @model_validator(mode="after")
    def require_phone_or_email(self) -> "ActivationStep2":
        if not (self.phone or "").strip() and not (self.email or "").strip():
            raise ValueError("At least one of phone or email is required")
        return self


class LoginRequest(BaseModel):
    """Login with phone or email (login field) + password."""

    login: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1, max_length=128)
    device_name: str = Field(default="", max_length=64)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    phone: str | None = None
    email: str | None = None
    level: int = 0


class DeviceInfo(BaseModel):
    device_id: str
    device_name: str
    last_active: str | None = None


class DeviceLimitError(BaseModel):
    code: str = "DEVICE_LIMIT_REACHED"
    message: str = "Account is in use on 3 devices. Log out on one device to continue."
    active_devices: list[DeviceInfo] = []
