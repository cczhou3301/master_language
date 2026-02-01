"""
User repository: query user by id, phone, email, phone_or_email; create user.
Also defines get_current_admin_user_id (FastAPI dependency using this repo).
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.const import UserLevel
from app.core.dal.repository.base import BaseRepository
from app.core.dal.repository.database import get_db
from app.models import User
from app.utils.auth_deps import get_current_user_id
from app.utils.id_generator import generate_bigint_id


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id: int) -> User | None:
        r = await self.session.execute(select(User).where(User.id == id))
        return r.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        r = await self.session.execute(select(User).where(User.phone == phone))
        return r.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        r = await self.session.execute(select(User).where(User.email == email))
        return r.scalar_one_or_none()

    async def get_by_phone_or_email(self, login: str) -> User | None:
        r = await self.session.execute(
            select(User).where(or_(User.phone == login, User.email == login))
        )
        return r.scalar_one_or_none()

    def create(
        self,
        *,
        phone: str | None = None,
        email: str | None = None,
        password_salt: str,
        password_hash: str,
    ) -> User:
        user = User(
            id=generate_bigint_id(),
            phone=phone,
            email=email,
            password_salt=password_salt,
            password_hash=password_hash,
        )
        self.add(user)
        return user


async def get_current_admin_user_id(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
) -> int:
    """Require valid access token and user.level == 'admin'. Returns user_id or 403."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or user.level != UserLevel.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ADMIN_REQUIRED", "message": "Admin access required."},
        )
    return user_id
