from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_bigint_id() -> int:
    """Generate a positive 64-bit id (BIGINT UNSIGNED). Use instead of auto-increment."""
    return uuid.uuid4().int % (2**64)


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )


class SoftDeleteMixin:
    """Soft delete: set deleted_at instead of hard delete. Filter with .where(Model.not_deleted())."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    @classmethod
    def not_deleted(cls):
        """Criterion for excluding soft-deleted rows: .where(Model.not_deleted())."""
        return cls.deleted_at.is_(None)


def set_soft_deleted(instance: SoftDeleteMixin) -> None:
    """Soft-delete: set deleted_at to now. Use instead of db.delete(instance)."""
    instance.deleted_at = utc_now()
