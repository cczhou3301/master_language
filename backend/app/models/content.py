from __future__ import annotations

from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True
    )  # e.g. YouTube id
    title_en: Mapped[str] = mapped_column(String(512), default="")
    title_zh: Mapped[str] = mapped_column(String(512), default="")
    thumbnail_url: Mapped[str] = mapped_column(String(1024), default="")
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    accent: Mapped[str] = mapped_column(
        String(32), default="american"
    )  # american, british, australian
    topic: Mapped[str] = mapped_column(
        String(64), default=""
    )  # travel, business, food, etc.

    subtitle_lines: Mapped[list["SubtitleLine"]] = relationship(
        "SubtitleLine", back_populates="video", order_by="start_ms"
    )


class SubtitleLine(Base, TimestampMixin):
    __tablename__ = "subtitle_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"), nullable=False)
    start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    text_en: Mapped[str] = mapped_column(Text, default="")
    text_zh: Mapped[str] = mapped_column(Text, default="")

    video: Mapped["Video"] = relationship("Video", back_populates="subtitle_lines")


class UserVocabulary(Base, TimestampMixin):
    __tablename__ = "user_vocabulary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    word: Mapped[str] = mapped_column(String(128), nullable=False)
    definition: Mapped[str] = mapped_column(Text, default="")
    source_subtitle_id: Mapped[int | None] = mapped_column(
        ForeignKey("subtitle_lines.id"), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="vocab")


class UserSentence(Base, TimestampMixin):
    __tablename__ = "user_sentences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subtitle_line_id: Mapped[int] = mapped_column(
        ForeignKey("subtitle_lines.id"), nullable=False
    )
    # Deep-link: video_id + start_ms for replay

    user: Mapped["User"] = relationship("User", back_populates="sentences")
