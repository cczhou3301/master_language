"""
Video feed and detail. Rate limiting: video_uid, video_ip. PRD Module 4, 2.
API calls service only; no direct DB or repository usage.
"""

from __future__ import annotations

from fastapi import Depends, Query

from app.core.dal import get_db
from app.core.router import video_router
from app.dto import VideoCard, VideoDetail
from app.service import video_service
from sqlalchemy.ext.asyncio import AsyncSession

router = video_router


@video_router.get("")
async def feed(
    session: AsyncSession = Depends(get_db),
    difficulty: int | None = Query(None, ge=1, le=5),
    accent: str | None = None,
    topic: str | None = None,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
) -> list[VideoCard]:
    """Video feed with filters. PRD 4.1, 4.2."""
    return await video_service.get_feed(
        session,
        difficulty=difficulty,
        accent=accent,
        topic=topic,
        limit=limit,
        offset=offset,
    )


@video_router.get("/{video_id}")
async def get_video(
    video_id: int,
    session: AsyncSession = Depends(get_db),
) -> VideoDetail | None:
    """Video detail with subtitle lines for intensive reading. PRD 2.2."""
    return await video_service.get_video_detail(session, video_id)
