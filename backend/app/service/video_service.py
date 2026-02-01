"""
Video service: feed and detail. Uses repositories.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dal.repository import VideoRepository, SubtitleLineRepository
from app.dto import VideoCard, VideoDetail, SubtitleLineSchema


async def get_feed(
    session: AsyncSession,
    *,
    difficulty: int | None = None,
    accent: str | None = None,
    topic: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[VideoCard]:
    """Video feed with filters. PRD 4.1, 4.2."""
    repo = VideoRepository(session)
    rows = await repo.list_(
        difficulty=difficulty,
        accent=accent,
        topic=topic,
        limit=limit,
        offset=offset,
    )
    return [
        VideoCard(
            id=v.id,
            external_id=v.external_id or "",
            title_en=v.title_en,
            title_zh=v.title_zh or None,
            thumbnail_url=v.thumbnail_url,
            duration_seconds=v.duration_seconds,
            difficulty=v.difficulty,
            accent=v.accent,
            topic=v.topic,
            completed=False,
        )
        for v in rows
    ]


async def get_video_detail(
    session: AsyncSession, video_id: int
) -> VideoDetail | None:
    """Video detail with subtitle lines. PRD 2.2."""
    video_repo = VideoRepository(session)
    line_repo = SubtitleLineRepository(session)

    v = await video_repo.get_by_id(video_id)
    if not v:
        return None

    lines = await line_repo.list_by_video_id(video_id)
    return VideoDetail(
        id=v.id,
        external_id=v.external_id or "",
        title_en=v.title_en,
        title_zh=v.title_zh or None,
        thumbnail_url=v.thumbnail_url,
        duration_seconds=v.duration_seconds,
        difficulty=v.difficulty,
        accent=v.accent,
        topic=v.topic,
        subtitle_lines=[
            SubtitleLineSchema(
                id=s.id,
                start_ms=s.start_ms,
                end_ms=s.end_ms,
                language=s.language,
                content=s.content or "",
            )
            for s in lines
        ],
    )
