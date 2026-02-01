"""
Video repository: get by id, list with optional filters (difficulty, accent, topic).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Video
from app.core.dal.repository.base import BaseRepository


class VideoRepository(BaseRepository[Video]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, video_id: int) -> Video | None:
        r = await self.session.execute(select(Video).where(Video.id == video_id))
        return r.scalar_one_or_none()

    async def list_(
        self,
        *,
        difficulty: int | None = None,
        accent: str | None = None,
        topic: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Video]:
        q = select(Video).limit(limit).offset(offset)
        if difficulty is not None:
            q = q.where(Video.difficulty == difficulty)
        if accent:
            q = q.where(Video.accent == accent)
        if topic:
            q = q.where(Video.topic == topic)
        r = await self.session.execute(q)
        return list(r.scalars().all())
