"""Permissions router - read-only catalogue access.

This module exposes only GET endpoints. No POST, PATCH, or DELETE endpoints
exist, enforcing the read-only contract at the routing level.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.permission import PermissionResponse
from app.services import permission_service

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    module: str | None = Query(
        default=None,
        description="Filter permissions by module (e.g., 'leads', 'accounts')",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[PermissionResponse]:
    """List all permissions, optionally filtered by module.

    Returns the full permission catalogue ordered by module and action.
    This endpoint is read-only — the catalogue is seeded at deployment time.
    """
    permissions = await permission_service.list_permissions(db, module=module)
    return [PermissionResponse.model_validate(p) for p in permissions]
