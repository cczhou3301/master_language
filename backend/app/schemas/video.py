from __future__ import annotations

from pydantic import BaseModel, Field


class VideoCard(BaseModel):
    id: int
    external_id: str
    title_en: str
    title_zh: str | None = None
    thumbnail_url: str
    duration_seconds: int
    difficulty: int  # 1-5
    accent: str
    topic: str
    completed: bool = False


class VideoFeedQuery(BaseModel):
    difficulty: int | None = None
    accent: str | None = None
    topic: str | None = None
    limit: int = Field(default=20, le=50)
    offset: int = Field(default=0, ge=0)


class SubtitleLineSchema(BaseModel):
    id: int
    start_ms: int
    end_ms: int
    language: str
    content: str


class VideoDetail(BaseModel):
    id: int
    external_id: str
    title_en: str
    title_zh: str | None = None
    thumbnail_url: str
    duration_seconds: int
    difficulty: int
    accent: str
    topic: str
    subtitle_lines: list[SubtitleLineSchema] = []
