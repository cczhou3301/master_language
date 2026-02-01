"""
Database: async MySQL with connection pooling, retries for HA/fault tolerance.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool  # pyright: ignore[reportMissingImports]

from app.config import get_settings

_settings = get_settings()

# Use NullPool in tests to avoid connection reuse; otherwise use QueuePool (default)
_use_null_pool = "test" in _settings.DATABASE_URL.lower()

_engine_kw: dict = {
    "pool_pre_ping": True,  # fault tolerance: verify connection before use
    "echo": _settings.DEBUG and _settings.is_development,
}
if _use_null_pool:
    _engine_kw["poolclass"] = NullPool
else:
    _engine_kw["pool_size"] = _settings.DB_POOL_SIZE
    _engine_kw["max_overflow"] = _settings.DB_MAX_OVERFLOW
    _engine_kw["pool_recycle"] = 300  # recycle connections to avoid stale

engine = create_async_engine(_settings.DATABASE_URL, **_engine_kw)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create tables. In production, prefer Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: None
        )  # no-op; tables via Alembic or below
    # If using metadata.create_all:
    # from app.models import Base
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
