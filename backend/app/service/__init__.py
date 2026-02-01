"""
Service layer: orchestrate repositories and other packages. API calls services only.
"""

from __future__ import annotations

from app.service import auth_service, user_service, video_service

__all__ = ["auth_service", "user_service", "video_service"]
