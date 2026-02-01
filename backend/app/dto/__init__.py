"""DTOs generated from IDL. Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""
from __future__ import annotations

from .auth_dto import (
    ActivationStep1,
    ActivationStep2,
    DeviceInfo,
    DeviceLimitError,
    GenerateActivationCodesRequest,
    GenerateActivationCodesResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
)
from .user_dto import LearningStats, UserProfile
from .video_dto import SubtitleLineSchema, VideoCard, VideoDetail, VideoFeedQuery

__all__ = [
    "ActivationStep1",
    "ActivationStep2",
    "DeviceInfo",
    "DeviceLimitError",
    "GenerateActivationCodesRequest",
    "GenerateActivationCodesResponse",
    "LoginRequest",
    "LoginResponse",
    "LogoutRequest",
    "RefreshRequest",
    "RefreshResponse",
    "LearningStats",
    "UserProfile",
    "SubtitleLineSchema",
    "VideoCard",
    "VideoDetail",
    "VideoFeedQuery",
]
