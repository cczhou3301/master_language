"""
Create DB tables. Run once in dev: python -m app.scripts.init_db
In production use Alembic migrations.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.dal import engine
from app.models import Base


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
