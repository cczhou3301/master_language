"""
Video feed and detail. Rate limiting: video_uid, video_ip. PRD Module 4, 2.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import rate_limit_video_uid, rate_limit_video_ip
from app.models import Video, SubtitleLine
from app.schemas.video import VideoCard, VideoFeedQuery, VideoDetail, SubtitleLineSchema

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", dependencies=[Depends(rate_limit_video_ip)])
async def feed(
    db: AsyncSession = Depends(get_db),
    difficulty: int | None = Query(None, ge=1, le=5),
    accent: str | None = None,
    topic: str | None = None,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
) -> list[VideoCard]:
    """Video feed with filters. PRD 4.1, 4.2. UID limit applied when auth middleware is on."""
    q = select(Video).limit(limit).offset(offset)
    if difficulty is not None:
        q = q.where(Video.difficulty == difficulty)
    if accent:
        q = q.where(Video.accent == accent)
    if topic:
        q = q.where(Video.topic == topic)
    r = await db.execute(q)
    rows = r.scalars().all()
    # TODO: join completion status when we have progress table
    return [
        VideoCard(
            id=v.id,
            external_id=v.external_id,
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


@router.get("/{video_id}", dependencies=[Depends(rate_limit_video_ip)])
async def get_video(
    video_id: int,
    db: AsyncSession = Depends(get_db),
) -> VideoDetail | None:
    """Video detail with subtitle lines for intensive reading. PRD 2.2."""
    r = await db.execute(select(Video).where(Video.id == video_id))
    v = r.scalar_one_or_none()
    if not v:
        return None
    r2 = await db.execute(
        select(SubtitleLine)
        .where(SubtitleLine.video_id == video_id)
        .order_by(SubtitleLine.start_ms)
    )
    lines = r2.scalars().all()
    return VideoDetail(
        id=v.id,
        external_id=v.external_id,
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
                text_en=s.text_en,
                text_zh=s.text_zh,
            )
            for s in lines
        ],
    )
