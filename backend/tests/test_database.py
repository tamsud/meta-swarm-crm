"""Tests for database configuration and foreign key enforcement."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, set_sqlite_pragma


@pytest.mark.asyncio
async def test_pragma_foreign_keys_enabled() -> None:
    """Verify that PRAGMA foreign_keys=ON is set on SQLite connections."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA foreign_keys"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1, "PRAGMA foreign_keys should be enabled (1)"

    await engine.dispose()


@pytest.mark.asyncio
async def test_foreign_key_violation_rejected() -> None:
    """Verify that FK violations are rejected when PRAGMA foreign_keys=ON."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        # Enable foreign keys
        await conn.execute(text("PRAGMA foreign_keys=ON"))

        # Create parent table
        await conn.execute(text("""
            CREATE TABLE parent (
                id INTEGER PRIMARY KEY
            )
        """))

        # Create child table with FK constraint
        await conn.execute(text("""
            CREATE TABLE child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER REFERENCES parent(id)
            )
        """))

        # Insert valid parent
        await conn.execute(text("INSERT INTO parent (id) VALUES (1)"))

        # Insert valid child (should succeed)
        await conn.execute(text("INSERT INTO child (id, parent_id) VALUES (1, 1)"))

        # Insert invalid child (FK violation - should fail)
        with pytest.raises(Exception) as exc_info:
            await conn.execute(text("INSERT INTO child (id, parent_id) VALUES (2, 999)"))

        assert "FOREIGN KEY constraint failed" in str(exc_info.value)

    await engine.dispose()
