"""Permissions router - read-only catalogue access.

This module exposes only GET endpoints. No POST, PATCH, or DELETE endpoints
exist, enforcing the read-only contract at the routing level.

Any authenticated user can read the permission catalogue.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.permission import PermissionResponse
from app.services import permission_service

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("")
async def list_permissions(
    module: str | None = Query(
        default=None,
        description="Filter permissions by module (e.g., 'leads', 'accounts')",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """List all permissions, optionally filtered by module.

    Returns the full permission catalogue ordered by module and action.
    This endpoint is read-only - the catalogue is seeded at deployment time.
    Requires authentication (any authenticated user can access).
    """
    permissions = await permission_service.list_permissions(db, module=module)
    items = [PermissionResponse.model_validate(p) for p in permissions]
    count = len(items)
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": count,
            "total": count,
            "offset": 0,
            "limit": count or 1,
        },
    }
