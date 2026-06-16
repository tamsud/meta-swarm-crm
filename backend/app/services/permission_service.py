"""Permission service - read-only catalogue access."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


async def list_permissions(
    db: AsyncSession,
    *,
    module: str | None = None,
) -> list[Permission]:
    """List all permissions, optionally filtered by module.

    Args:
        db: Async database session.
        module: Optional module name to filter by (e.g., "leads", "accounts").

    Returns:
        List of Permission objects, ordered by module then action.
    """
    stmt = select(Permission).order_by(Permission.module, Permission.action)

    if module is not None:
        stmt = stmt.where(Permission.module == module)

    result = await db.execute(stmt)
    return list(result.scalars().all())
