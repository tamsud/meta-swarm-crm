"""User service - CRUD operations with business rules."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.core.security.passwords import hash_password, verify_password
from app.exceptions import (
    AccountInactiveError,
    EmailConflictError,
    InvalidCredentialsError,
    InvalidRoleIdError,
    LastAdminLockoutError,
    UserNotFoundError,
)
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserSelfUpdate, UserUpdate

settings = get_settings()


async def _validate_role_id(db: AsyncSession, role_id: int) -> None:
    """Validate that role_id exists in the roles table."""
    stmt = select(Role.id).where(Role.id == role_id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        raise InvalidRoleIdError(role_id)


async def _get_admin_role_id(db: AsyncSession) -> int | None:
    """Get the ID of the Admin role."""
    stmt = select(Role.id).where(Role.name == "Admin")
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _count_active_admins(db: AsyncSession, admin_role_id: int) -> int:
    """Count the number of active users with the Admin role."""
    stmt = select(func.count()).select_from(User).where(
        User.role_id == admin_role_id,
        User.is_active == True,  # noqa: E712
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def _check_last_admin_lockout(
    db: AsyncSession,
    user: User,
    new_is_active: bool | None,
    new_role_id: int | None,
) -> None:
    """Check if the update would leave zero active Admins.

    Raises LastAdminLockoutError if the change would remove the last active Admin.
    """
    admin_role_id = await _get_admin_role_id(db)
    if admin_role_id is None:
        # No Admin role exists (shouldn't happen in normal operation)
        return

    # Check if this user is currently an active Admin
    is_currently_active_admin = (
        user.role_id == admin_role_id and user.is_active
    )

    if not is_currently_active_admin:
        # User is not currently an active Admin, no lockout risk
        return

    # Determine if the update would make them no longer an active Admin
    will_deactivate = new_is_active is False
    will_change_role = new_role_id is not None and new_role_id != admin_role_id

    if not (will_deactivate or will_change_role):
        # No change that affects Admin status
        return

    # Count current active Admins
    active_admin_count = await _count_active_admins(db, admin_role_id)

    if active_admin_count <= 1:
        # This is the last active Admin
        raise LastAdminLockoutError()


async def create_user(
    db: AsyncSession,
    user_data: UserCreate,
) -> User:
    """Create a new user with hashed password.

    Args:
        db: Async database session.
        user_data: User creation data including email, password, role_id.

    Returns:
        The created User with role loaded.

    Raises:
        EmailConflictError: If a user with the same email exists (case-insensitive).
        InvalidRoleIdError: If role_id doesn't exist.
    """
    # Validate role_id exists
    await _validate_role_id(db, user_data.role_id)

    # Hash the password
    hashed = hash_password(user_data.password)

    user = User(
        email=user_data.email.lower(),  # Normalize email to lowercase
        hashed_password=hashed,
        display_name=user_data.display_name,
        role_id=user_data.role_id,
    )
    db.add(user)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise EmailConflictError()

    await db.commit()
    await db.refresh(user)

    # Load the role relationship
    return await get_user(db, user.id)


async def get_user(
    db: AsyncSession,
    user_id: int,
) -> User:
    """Get a user by ID with role loaded.

    Args:
        db: Async database session.
        user_id: The user ID to fetch.

    Returns:
        The User with role loaded.

    Raises:
        UserNotFoundError: If user doesn't exist.
    """
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.role))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError()

    return user


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """Get a user by email (case-insensitive).

    Args:
        db: Async database session.
        email: The email to look up.

    Returns:
        The User if found, None otherwise.
    """
    stmt = (
        select(User)
        .where(func.lower(User.email) == func.lower(email))
        .options(selectinload(User.role))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession,
    *,
    search: str | None = None,
    role_id_filter: int | None = None,
    is_active_filter: bool | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[User], int]:
    """List users with optional search, filtering, and pagination.

    Args:
        db: Async database session.
        search: Optional partial email/display_name search (case-insensitive).
        role_id_filter: Optional filter by role ID.
        is_active_filter: Optional filter by active status.
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (defaults to Settings.DEFAULT_PAGE_SIZE).

    Returns:
        Tuple of (list of User objects, total count).
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    # Build base query with optional filters
    base_query = select(User)

    if search:
        search_pattern = f"%{search}%"
        base_query = base_query.where(
            (func.lower(User.email).like(func.lower(search_pattern)))
            | (func.lower(User.display_name).like(func.lower(search_pattern)))
        )

    if role_id_filter is not None:
        base_query = base_query.where(User.role_id == role_id_filter)

    if is_active_filter is not None:
        base_query = base_query.where(User.is_active == is_active_filter)

    # Count query
    count_stmt = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Data query with pagination and role loading
    stmt = (
        base_query
        .options(selectinload(User.role))
        .order_by(User.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    users = list(result.scalars().all())

    return users, total


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_data: UserUpdate,
) -> User:
    """Update an existing user (Admin operation).

    Args:
        db: Async database session.
        user_id: The user ID to update.
        user_data: Updated user data (role_id, is_active, display_name).

    Returns:
        The updated User with role loaded.

    Raises:
        UserNotFoundError: If user doesn't exist.
        InvalidRoleIdError: If new role_id doesn't exist.
        LastAdminLockoutError: If update would leave zero active Admins.
    """
    user = await get_user(db, user_id)

    # Validate new role_id if provided
    if user_data.role_id is not None:
        await _validate_role_id(db, user_data.role_id)

    # Check last Admin lockout before making changes
    await _check_last_admin_lockout(
        db,
        user,
        user_data.is_active,
        user_data.role_id,
    )

    # Apply updates
    if user_data.role_id is not None:
        user.role_id = user_data.role_id

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.display_name is not None:
        user.display_name = user_data.display_name

    # Update timestamp
    user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    # Reload with role relationship
    return await get_user(db, user_id)


async def update_self(
    db: AsyncSession,
    user_id: int,
    user_data: UserSelfUpdate,
) -> User:
    """Update the current user's own profile (limited to display_name).

    Args:
        db: Async database session.
        user_id: The user ID to update.
        user_data: Updated user data (display_name only).

    Returns:
        The updated User with role loaded.

    Raises:
        UserNotFoundError: If user doesn't exist.
    """
    user = await get_user(db, user_id)

    if user_data.display_name is not None:
        user.display_name = user_data.display_name
        user.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(user)

    return await get_user(db, user_id)


async def verify_credentials(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    """Verify user credentials for login.

    Args:
        db: Async database session.
        email: The user's email.
        password: The user's password (plaintext).

    Returns:
        The User if credentials are valid and account is active.

    Raises:
        InvalidCredentialsError: If email not found or password doesn't match.
        AccountInactiveError: If user exists but is deactivated.
    """
    user = await get_user_by_email(db, email)

    if user is None:
        raise InvalidCredentialsError()

    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()

    if not user.is_active:
        raise AccountInactiveError()

    return user
