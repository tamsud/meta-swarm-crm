"""Role service - CRUD operations with business rules."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import (
    DuplicateRoleNameError,
    InvalidPermissionIdsError,
    RoleNotFoundError,
    SystemRoleImmutableError,
)
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.schemas.role import RoleCreate, RoleUpdate


async def _validate_permission_ids(
    db: AsyncSession,
    permission_ids: list[int],
) -> None:
    """Validate all permission_ids exist in the permissions table."""
    if not permission_ids:
        return

    stmt = select(Permission.id).where(Permission.id.in_(permission_ids))
    result = await db.execute(stmt)
    existing_ids = set(result.scalars().all())
    requested_ids = set(permission_ids)
    invalid_ids = requested_ids - existing_ids

    if invalid_ids:
        raise InvalidPermissionIdsError(sorted(invalid_ids))


async def _sync_role_permissions(
    db: AsyncSession,
    role: Role,
    permission_ids: list[int],
) -> None:
    """Replace role's permissions with the given set (diff-based)."""
    current_ids = {rp.permission_id for rp in role.role_permissions}
    new_ids = set(permission_ids)

    to_remove = current_ids - new_ids
    to_add = new_ids - current_ids

    for rp in list(role.role_permissions):
        if rp.permission_id in to_remove:
            await db.delete(rp)

    for perm_id in to_add:
        db.add(RolePermission(role_id=role.id, permission_id=perm_id))


async def create_role(
    db: AsyncSession,
    role_data: RoleCreate,
) -> Role:
    """Create a new role with the specified permissions.

    Args:
        db: Async database session.
        role_data: Role creation data including name and permission_ids.

    Returns:
        The created Role with permissions loaded.

    Raises:
        InvalidPermissionIdsError: If any permission_id doesn't exist.
        DuplicateRoleNameError: If a role with the same name exists.
    """
    await _validate_permission_ids(db, role_data.permission_ids)

    role = Role(
        name=role_data.name,
        description=role_data.description,
        is_system=False,
    )
    db.add(role)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise DuplicateRoleNameError()

    for perm_id in role_data.permission_ids:
        db.add(RolePermission(role_id=role.id, permission_id=perm_id))

    await db.commit()

    return await get_role(db, role.id)


async def get_role(
    db: AsyncSession,
    role_id: int,
) -> Role:
    """Get a role by ID with permissions loaded.

    Args:
        db: Async database session.
        role_id: The role ID to fetch.

    Returns:
        The Role with permissions loaded.

    Raises:
        RoleNotFoundError: If role doesn't exist.
    """
    stmt = (
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
    )
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()

    if role is None:
        raise RoleNotFoundError()

    return role


async def update_role(
    db: AsyncSession,
    role_id: int,
    role_data: RoleUpdate,
) -> Role:
    """Update an existing role.

    Args:
        db: Async database session.
        role_id: The role ID to update.
        role_data: Updated role data.

    Returns:
        The updated Role with permissions loaded.

    Raises:
        RoleNotFoundError: If role doesn't exist.
        SystemRoleImmutableError: If attempting to modify a system role.
        InvalidPermissionIdsError: If any permission_id doesn't exist.
        DuplicateRoleNameError: If new name conflicts with existing role.
    """
    role = await get_role(db, role_id)

    if role.is_system:
        if role_data.name is not None or role_data.permission_ids is not None:
            raise SystemRoleImmutableError()

    if role_data.name is not None:
        role.name = role_data.name

    if role_data.description is not None:
        role.description = role_data.description

    if role_data.permission_ids is not None:
        await _validate_permission_ids(db, role_data.permission_ids)
        await _sync_role_permissions(db, role, role_data.permission_ids)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise DuplicateRoleNameError()

    return await get_role(db, role_id)


async def delete_role(
    db: AsyncSession,
    role_id: int,
) -> None:
    """Delete a role.

    Args:
        db: Async database session.
        role_id: The role ID to delete.

    Raises:
        RoleNotFoundError: If role doesn't exist.
        SystemRoleImmutableError: If attempting to delete a system role.
        RoleHasUsersError: If role has assigned users (deferred until Users module).
    """
    role = await get_role(db, role_id)

    if role.is_system:
        raise SystemRoleImmutableError()

    await db.delete(role)
    await db.commit()


async def list_roles(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 100,
) -> tuple[list[Role], int]:
    """List all roles with pagination.

    Returns roles with permission_count computed in a single query.
    user_count is 0 until the Users module is implemented.

    Args:
        db: Async database session.
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (default 100).

    Returns:
        Tuple of (list of Role objects, total count).
    """
    count_stmt = select(func.count()).select_from(Role)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    stmt = (
        select(Role)
        .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        .order_by(Role.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    roles = list(result.scalars().all())

    return roles, total
