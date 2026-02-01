"""
Repository: database session (MySQL), *Repository classes, and auth deps (admin check).
"""

from __future__ import annotations

from app.core.dal.repository.database import get_db, engine, AsyncSessionLocal, init_db
from app.core.dal.repository.base import BaseRepository
from app.core.dal.repository.user_repository import UserRepository, get_current_admin_user_id
from app.core.dal.repository.activation_code_repository import ActivationCodeRepository
from app.core.dal.repository.user_device_repository import UserDeviceRepository
from app.core.dal.repository.video_repository import VideoRepository
from app.core.dal.repository.subtitle_line_repository import SubtitleLineRepository

__all__ = [
    "get_db",
    "engine",
    "AsyncSessionLocal",
    "init_db",
    "BaseRepository",
    "UserRepository",
    "ActivationCodeRepository",
    "UserDeviceRepository",
    "VideoRepository",
    "SubtitleLineRepository",
    "get_current_admin_user_id",
]
