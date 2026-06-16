"""Users router - CRUD endpoints for user management.

Permission codes required (from 0003_seed_permissions.py):
- users:manage (Admin-only for all CRUD operations on other users)

IMPORTANT: There is NO DELETE endpoint. Users are deactivated via PATCH
with is_active=false (soft deactivation only).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security.dependencies import get_current_user, require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])
settings = get_settings()


# -----------------------------------------------------------------------------
# /me endpoints - must be defined BEFORE /{user_id} to avoid path collision
# -----------------------------------------------------------------------------


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get the current authenticated user's profile.

    Returns the user's full profile including role details.
    Only requires authentication, no specific permission needed.
    """
    # Reload the user with role details (current_user already has role loaded)
    user = await user_service.get_user(db, current_user.id)
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserSelfUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update the current authenticated user's profile.

    Users can only update their own display_name. Attempting to update
    other fields (role_id, is_active, etc.) will return 422.
    Only requires authentication, no specific permission needed.
    """
    user = await user_service.update_user(db, current_user.id, user_data)
    return UserResponse.model_validate(user)


# -----------------------------------------------------------------------------
# Admin endpoints - require users:manage permission
# -----------------------------------------------------------------------------


@router.get("")
async def list_users(
    search: str | None = Query(
        default=None,
        max_length=256,
        description="Partial email or display_name search (case-insensitive)",
    ),
    role_id: int | None = Query(
        default=None,
        description="Filter by role ID",
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter by active status",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=None,
        ge=1,
        le=1000,
        description="Max records to return (defaults to DEFAULT_PAGE_SIZE)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:manage")),
) -> dict:
    """List all users with search, filtering, and pagination.

    Admin-only endpoint. Non-Admin users will receive 403.
    Requires users:manage permission.

    Query parameters:
    - search: Partial match on email or display_name (case-insensitive)
    - role_id: Filter by role ID
    - is_active: Filter by active status (true/false)
    - offset: Pagination offset
    - limit: Max records per page
    """
    effective_limit = limit if limit is not None else settings.DEFAULT_PAGE_SIZE

    users, total = await user_service.list_users(
        db,
        search=search,
        role_id_filter=role_id,
        is_active_filter=is_active,
        offset=offset,
        limit=effective_limit,
    )
    items = [UserListResponse.model_validate(u) for u in users]
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": effective_limit,
        },
    }


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:manage")),
) -> UserResponse:
    """Create a new user.

    Admin-only endpoint. Requires users:manage permission.

    The password is hashed before storage. Email is normalized to lowercase.

    Returns:
        201: User created successfully with full profile including role.
        409: Email already exists (DUPLICATE_EMAIL).
        422: Invalid role_id (INVALID_ROLE_ID) or validation error.
    """
    user = await user_service.create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:manage")),
) -> UserResponse:
    """Get a single user by ID.

    Admin-only endpoint. Requires users:manage permission.

    Returns:
        200: User profile with full role details.
        404: User not found (USER_NOT_FOUND).
    """
    user = await user_service.get_user(db, user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:manage")),
) -> UserResponse:
    """Update an existing user.

    Admin-only endpoint. Requires users:manage permission.

    Updatable fields:
    - role_id: Change user's role
    - is_active: Activate/deactivate user (soft delete)
    - display_name: Update display name

    Note: Users are deactivated by setting is_active=false, not deleted.
    There is no DELETE endpoint for users.

    Returns:
        200: Updated user profile with full role details.
        400: Cannot deactivate or change role of last active Admin (LAST_ADMIN_LOCKOUT).
        404: User not found (USER_NOT_FOUND).
        422: Invalid role_id (INVALID_ROLE_ID) or validation error.
    """
    user = await user_service.update_user(db, user_id, user_data)
    return UserResponse.model_validate(user)
