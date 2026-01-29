from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    phone: str | None = None
    email: str | None = None
    level: int = 0
    # no password or sensitive fields


class LearningStats(BaseModel):
    total_sentences_learned: int = 0
    total_videos_completed: int = 0
    study_duration_minutes: int = 0
    current_streak_days: int = 0
