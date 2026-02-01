"""
Base repository: session-scoped, common get/add/flush. All queries go through repository layer.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Session-scoped repository. Subclass per entity."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def get_by_id(self, model: type[ModelT], id: int) -> ModelT | None:
        """Load entity by primary key. Returns None if not found."""
        r = await self._session.execute(select(model).where(model.id == id))
        return r.scalar_one_or_none()

    def add(self, instance: ModelT) -> None:
        """Add entity to session (flush/commit done by caller or get_db)."""
        self._session.add(instance)

    async def flush(self) -> None:
        """Flush pending changes."""
        await self._session.flush()
