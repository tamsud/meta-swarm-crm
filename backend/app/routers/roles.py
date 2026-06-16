"""Roles router - CRUD endpoints for role management.

Note: This router is initially implemented without permission gating.
Authentication module (WU-AUTH-3) will add require_permission("roles:manage")
to all endpoints when it's built.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import (
    AppException,
    DuplicateRoleNameError,
    InvalidPermissionIdsError,
    RoleHasUsersError,
    RoleNotFoundError,
    SystemRoleImmutableError,
)
from app.schemas.role import RoleCreate, RoleListResponse, RoleResponse, RoleUpdate
from app.services import role_service

router = APIRouter(prefix="/roles", tags=["roles"])


def _map_exception_to_http(exc: AppException) -> HTTPException:
    """Map application exceptions to HTTP responses."""
    detail = {"error_code": exc.error_code, "message": exc.detail}
    if exc.extra:
        detail.update(exc.extra)
    return HTTPException(status_code=exc.status_code, detail=detail)


@router.get("", response_model=list[RoleListResponse])
async def list_roles(
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
) -> list[RoleListResponse]:
    """List all roles with pagination.

    Returns roles with permission_count and user_count.
    System roles are marked with is_system=true.
    """
    roles, _total = await role_service.list_roles(db, offset=offset, limit=limit)
    return [RoleListResponse.model_validate(r) for r in roles]


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """Create a new custom role with the specified permissions.

    System roles cannot be created via this endpoint.
    """
    try:
        role = await role_service.create_role(db, role_data)
        return RoleResponse.model_validate(role)
    except (InvalidPermissionIdsError, DuplicateRoleNameError) as exc:
        raise _map_exception_to_http(exc)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """Get a single role by ID with full permission details."""
    try:
        role = await role_service.get_role(db, role_id)
        return RoleResponse.model_validate(role)
    except RoleNotFoundError as exc:
        raise _map_exception_to_http(exc)


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """Update an existing role.

    System roles cannot have their name or permissions modified.
    Only description updates are allowed for system roles.
    """
    try:
        role = await role_service.update_role(db, role_id, role_data)
        return RoleResponse.model_validate(role)
    except (
        RoleNotFoundError,
        SystemRoleImmutableError,
        InvalidPermissionIdsError,
        DuplicateRoleNameError,
    ) as exc:
        raise _map_exception_to_http(exc)


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a custom role.

    System roles cannot be deleted.
    Roles with assigned users cannot be deleted (returns 409).
    """
    try:
        await role_service.delete_role(db, role_id)
    except (RoleNotFoundError, SystemRoleImmutableError, RoleHasUsersError) as exc:
        raise _map_exception_to_http(exc)
