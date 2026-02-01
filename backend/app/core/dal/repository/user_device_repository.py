"""
UserDevice repository: list active by user_id, add device, mark logged_out.
Only devices with status='active' count toward device limit; logout sets status='logged_out'.
"""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserDevice
from app.core.dal.repository.base import BaseRepository
from app.utils.id_generator import generate_bigint_id

STATUS_ACTIVE = "active"
STATUS_LOGGED_OUT = "logged_out"


class UserDeviceRepository(BaseRepository[UserDevice]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user_id(self, user_id: int) -> list[UserDevice]:
        """List all devices for this user (active and logged_out). Use for login to find existing device and reactivate if needed."""
        r = await self.session.execute(
            select(UserDevice).where(UserDevice.user_id == user_id)
        )
        return list(r.scalars().all())

    async def list_active_by_user_id(self, user_id: int) -> list[UserDevice]:
        """List only active devices (for device limit count and error response)."""
        r = await self.session.execute(
            select(UserDevice).where(
                UserDevice.user_id == user_id,
                UserDevice.status == STATUS_ACTIVE,
            )
        )
        return list(r.scalars().all())

    async def find_by_user_and_device(
        self, user_id: int, device_id: str
    ) -> UserDevice | None:
        """Find one row by user_id and device_id (any status)."""
        r = await self.session.execute(
            select(UserDevice).where(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id,
            )
        )
        return r.scalar_one_or_none()

    def add_device(
        self,
        *,
        user_id: int,
        device_id: str,
        device_name: str,
        last_active_at: str,
    ) -> UserDevice:
        dev = UserDevice(
            id=generate_bigint_id(),
            user_id=user_id,
            device_id=device_id,
            device_name=device_name,
            last_active_at=last_active_at,
            status=STATUS_ACTIVE,
        )
        self.add(dev)
        return dev

    async def mark_logged_out(self, user_id: int, device_id: str) -> None:
        """Set status='logged_out' for this user's device. Idempotent."""
        await self.session.execute(
            update(UserDevice)
            .where(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id,
            )
            .values(status=STATUS_LOGGED_OUT)
        )

    async def reactivate_device(
        self,
        user_id: int,
        device_id: str,
        device_name: str,
        last_active_at: str,
    ) -> bool:
        """Set status='active' and update name/last_active for existing row. Returns True if updated."""
        r = await self.session.execute(
            update(UserDevice)
            .where(
                UserDevice.user_id == user_id,
                UserDevice.device_id == device_id,
            )
            .values(
                status=STATUS_ACTIVE,
                device_name=device_name,
                last_active_at=last_active_at,
            )
        )
        return getattr(r, "rowcount", 0) > 0
