"""
ActivationCode repository: get by code; create (batch generate).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.const import ActivationCodeStatus
from app.models import ActivationCode
from app.core.dal.repository.base import BaseRepository
from app.utils.id_generator import generate_bigint_id


class ActivationCodeRepository(BaseRepository[ActivationCode]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_code(self, code: str) -> ActivationCode | None:
        r = await self.session.execute(select(ActivationCode).where(ActivationCode.code == code))
        return r.scalar_one_or_none()

    def create_code(self, code: str) -> ActivationCode:
        """Create one activation code (status=unused). Caller flushes/commits."""
        ac = ActivationCode(
            id=generate_bigint_id(),
            code=code,
            status=ActivationCodeStatus.UNUSED,
        )
        self.session.add(ac)
        return ac
