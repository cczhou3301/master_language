from __future__ import annotations

from sqlalchemy import String, Boolean, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import Base, TimestampMixin


class ActivationCodeStatus(str, enum.Enum):
    UNUSED = "unused"
    USED = "used"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(
        String(11), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    devices: Mapped[list["UserDevice"]] = relationship(
        "UserDevice", back_populates="user", cascade="all, delete-orphan"
    )
    vocab: Mapped[list["UserVocabulary"]] = relationship(
        "UserVocabulary", back_populates="user"
    )
    sentences: Mapped[list["UserSentence"]] = relationship(
        "UserSentence", back_populates="user"
    )


class ActivationCode(Base, TimestampMixin):
    __tablename__ = "activation_codes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default=ActivationCodeStatus.UNUSED.value
    )
    used_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )


class UserDevice(Base, TimestampMixin):
    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
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
