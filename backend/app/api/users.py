"""
User profile and learning stats. PRD Module 5.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User, UserVocabulary, UserSentence
from app.schemas.user import UserProfile, LearningStats

# Placeholder: in real app, use JWT dependency to set request.state.user_id
# from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


async def _get_current_user_id() -> int:
    """Stub: replace with JWT auth dependency that sets request.state.user_id."""
    return 1


@router.get("/me")
async def me(db: AsyncSession = Depends(get_db)) -> UserProfile:
    uid = await _get_current_user_id()
    r = await db.execute(select(User).where(User.id == uid).where(User.not_deleted()))
    u = r.scalar_one_or_none()
    if not u:
        from fastapi import HTTPException

        raise HTTPException(401, "Not found")
    return UserProfile(id=u.id, phone=u.phone, email=u.email, level=u.level)


@router.get("/me/stats")
async def learning_stats(db: AsyncSession = Depends(get_db)) -> LearningStats:
    uid = await _get_current_user_id()
    # Stub: PRD 5.1 - sentences learned, videos completed, study duration, streak
    return LearningStats(
        total_sentences_learned=0,
        total_videos_completed=0,
        study_duration_minutes=0,
        current_streak_days=0,
    )
