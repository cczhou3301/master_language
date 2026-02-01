"""DTOs generated from IDL (user_pb2). Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""
from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Generated from idl message."""
    id: int = 0
    phone: str | None = None
    email: str | None = None
    level: str = ""


class LearningStats(BaseModel):
    """Generated from idl message."""
    total_sentences_learned: int = 0
    total_videos_completed: int = 0
    study_duration_minutes: int = 0
    current_streak_days: int = 0
