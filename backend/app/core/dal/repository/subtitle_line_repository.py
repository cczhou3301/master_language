"""
SubtitleLine repository: list by video_id ordered by start_ms.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SubtitleLine
from app.core.dal.repository.base import BaseRepository


class SubtitleLineRepository(BaseRepository[SubtitleLine]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_video_id(self, video_id: int) -> list[SubtitleLine]:
        r = await self.session.execute(
            select(SubtitleLine)
            .where(SubtitleLine.video_id == video_id)
            .order_by(SubtitleLine.start_ms)
        )
        return list(r.scalars().all())
