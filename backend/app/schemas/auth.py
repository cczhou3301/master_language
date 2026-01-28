from __future__ import annotations

from pydantic import BaseModel, Field


class ActivationStep1(BaseModel):
    code: str = Field(..., min_length=4, max_length=32)


class ActivationStep2(BaseModel):
    code: str = Field(..., min_length=4, max_length=32)
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    password: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1, max_length=128)
    device_name: str = Field(default="", max_length=64)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    phone: str


class DeviceInfo(BaseModel):
    device_id: str
    device_name: str
    last_active: str | None = None


class DeviceLimitError(BaseModel):
    code: str = "DEVICE_LIMIT_REACHED"
    message: str = "Account is in use on 3 devices. Log out on one device to continue."
    active_devices: list[DeviceInfo] = []
