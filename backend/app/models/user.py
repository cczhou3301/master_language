from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SoftDeleteMixin, TimestampMixin, generate_bigint_id

if TYPE_CHECKING:
    from .content import UserVocabulary, UserSentence


class ActivationCodeStatus(str, enum.Enum):
    UNUSED = "unused"
    USED = "used"


class UserLevel:
    """User level for benefits/rights. Higher = more privileges."""

    FREE = 0
    BASIC = 1
    PREMIUM = 2
    ADMIN = 9


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, default=generate_bigint_id
    )
    phone: Mapped[str | None] = mapped_column(
        String(32), unique=True, index=True, nullable=True
    )  # can be >11 chars (e.g. international)
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    level: Mapped[int] = mapped_column(Integer, default=UserLevel.FREE)

    devices: Mapped[list["UserDevice"]] = relationship(
        "UserDevice", back_populates="user", cascade="all, delete-orphan"
    )
    vocab: Mapped[list["UserVocabulary"]] = relationship(
        "UserVocabulary", back_populates="user"
    )
    sentences: Mapped[list["UserSentence"]] = relationship(
        "UserSentence", back_populates="user"
    )


class ActivationCode(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "activation_codes"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, default=generate_bigint_id
    )
    code: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default=ActivationCodeStatus.UNUSED.value
    )
    used_by_user_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id"), nullable=True
    )


class UserDevice(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, default=generate_bigint_id
    )
    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(
        String(128), nullable=False
    )  # client-generated stable id
    device_name: Mapped[str] = mapped_column(
        String(64), default=""
    )  # e.g. "Phone (Android)"
    last_active_at: Mapped[str] = mapped_column(
        String(32), default=""
    )  # ISO ts for display

    user: Mapped["User"] = relationship("User", back_populates="devices")
