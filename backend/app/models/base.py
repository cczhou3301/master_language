"""Models: Base only. No mixins. ID generator in app.utils."""
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
