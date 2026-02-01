"""
User profile and learning stats. PRD Module 5.
Protected by access token (get_current_user_id). API calls service only.
"""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dal import get_db
from app.core.router import user_router
from app.utils.auth_deps import get_current_user_id
from app.dto import UserProfile, LearningStats
from app.service import user_service

router = user_router


@user_router.get("/me")
async def me(
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> UserProfile:
    return await user_service.get_profile(session, user_id)


@user_router.get("/me/stats")
async def learning_stats(
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> LearningStats:
    return await user_service.get_learning_stats(session, user_id)
