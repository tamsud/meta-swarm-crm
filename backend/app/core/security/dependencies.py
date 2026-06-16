"""FastAPI dependencies for authentication and authorization."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security.jwt import decode_access_token
from app.database import get_db
from app.exceptions import (
    AccountInactiveError,
    InsufficientPermissionsError,
    InvalidTokenError,
    TokenExpiredError,
)
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from the JWT token.

    Loads User with Role and Permissions in a single query (no N+1).

    Args:
        token: JWT access token from Authorization header.
        db: Async database session.

    Returns:
        The authenticated User with role and permissions loaded.

    Raises:
        HTTPException 401: If token is missing, invalid, expired,
            or user account is inactive.
    """
    # Decode and validate the token
    try:
        payload = decode_access_token(token)
    except TokenExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Extract user_id from token payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert to int (JWT stores as string)
    try:
        user_id = int(user_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Load user with role and permissions in a single query
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.role)
            .selectinload(Role.role_permissions)
            .selectinload(RolePermission.permission)
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountInactiveError.detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(permission_code: str) -> Callable:
    """Factory that returns a dependency checking for a specific permission.

    Usage:
        @router.post("/", dependencies=[Depends(require_permission("accounts:create"))])
        async def create_account(...): ...

        # Or to get the user:
        @router.post("/")
        async def create_account(
            current_user: User = Depends(require_permission("accounts:create")),
        ): ...

    Args:
        permission_code: The permission code to check (e.g., "accounts:create").

    Returns:
        A FastAPI dependency that validates the permission and returns the user.

    Raises:
        HTTPException 403: If user lacks the required permission.
    """

    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """Check if the current user has the required permission."""
        # Get the set of permission codes the user has
        user_permission_codes = {
            rp.permission.code for rp in current_user.role.role_permissions
        }

        if permission_code not in user_permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=InsufficientPermissionsError(permission_code).detail,
            )

        return current_user

    return permission_checker
