"""DTOs generated from IDL (video_pb2). Do not edit by hand. Regenerate: python scripts/gen_dto_from_idl.py"""
from __future__ import annotations

from pydantic import BaseModel, Field


class VideoCard(BaseModel):
    """Generated from idl message."""
    id: int = 0
    external_id: str = ""
    title_en: str = ""
    title_zh: str | None = None
    thumbnail_url: str = ""
    duration_seconds: int = 0
    difficulty: int = 0
    accent: str = ""
    topic: str = ""
    completed: bool = False


class VideoFeedQuery(BaseModel):
    """Generated from idl message."""
    difficulty: int | None = None
    accent: str | None = None
    topic: str | None = None
    limit: int = 0
    offset: int = 0


class SubtitleLineSchema(BaseModel):
    """Generated from idl message."""
    id: int = 0
    start_ms: int = 0
    end_ms: int = 0
    language: str = ""
    content: str = ""


class VideoDetail(BaseModel):
    """Generated from idl message."""
    id: int = 0
    external_id: str = ""
    title_en: str = ""
    title_zh: str | None = None
    thumbnail_url: str = ""
    duration_seconds: int = 0
    difficulty: int = 0
    accent: str = ""
    topic: str = ""
    subtitle_lines: list[SubtitleLineSchema] = Field(default_factory=list)
