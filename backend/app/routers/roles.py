"""Roles router - CRUD endpoints for role management.

Permission codes required (from 0003_seed_permissions.py):
- roles:read (for list and get endpoints)
- roles:manage (for create, update, delete endpoints)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user, require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.role import RoleCreate, RoleListResponse, RoleResponse, RoleUpdate
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("")
async def list_roles(
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:read")),
) -> dict:
    """List all roles with pagination.

    Returns roles with permission_count and user_count.
    System roles are marked with is_system=true.
    Requires roles:read permission.
    """
    roles, total = await role_service.list_roles(db, offset=offset, limit=limit)
    items = [RoleListResponse.model_validate(r) for r in roles]
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:manage")),
) -> RoleResponse:
    """Create a new custom role with the specified permissions.

    System roles cannot be created via this endpoint.
    Requires roles:manage permission.
    """
    role = await role_service.create_role(db, role_data)
    return RoleResponse.model_validate(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:read")),
) -> RoleResponse:
    """Get a single role by ID with full permission details.

    Requires roles:read permission.
    """
    role = await role_service.get_role(db, role_id)
    return RoleResponse.model_validate(role)


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:manage")),
) -> RoleResponse:
    """Update an existing role.

    System roles cannot have their name or permissions modified.
    Only description updates are allowed for system roles.
    Requires roles:manage permission.
    """
    role = await role_service.update_role(db, role_id, role_data)
    return RoleResponse.model_validate(role)


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("roles:manage")),
) -> None:
    """Delete a custom role.

    System roles cannot be deleted.
    Roles with assigned users cannot be deleted (returns 409).
    Requires roles:manage permission.
    """
    await role_service.delete_role(db, role_id)
