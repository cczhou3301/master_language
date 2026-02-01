"""
User service: profile and learning stats. Uses repositories.
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dal.repository import UserRepository
from app.dto import UserProfile, LearningStats


async def get_profile(session: AsyncSession, user_id: int) -> UserProfile:
    """Get current user profile by id."""
    repo = UserRepository(session)
    u = await repo.get_by_id(user_id)
    if not u:
        raise HTTPException(401, "Not found")
    return UserProfile(
        id=u.id,
        phone=u.phone,
        email=u.email,
        level=u.level,
    )


async def get_learning_stats(session: AsyncSession, user_id: int) -> LearningStats:
    """Get learning stats. PRD 5.1 - placeholder until progress tables exist."""
    # Stub: later use progress/vocabulary repositories
    return LearningStats(
        total_sentences_learned=0,
        total_videos_completed=0,
        study_duration_minutes=0,
        current_streak_days=0,
    )
