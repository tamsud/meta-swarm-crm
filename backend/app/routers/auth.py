"""Authentication router - login and current user endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user
from app.core.security.jwt import create_access_token
from app.database import get_db
from app.models.user import User
from app.schemas.role import RoleResponse
from app.schemas.user import UserResponse
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Request body for login endpoint."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """Response body for successful login."""

    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    """Response body for /me endpoint with user, role, and permissions."""

    user: UserResponse
    role: RoleResponse
    permissions: list[str]


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user and return JWT token.

    Validates email/password credentials and returns a JWT access token
    in the response body (never as a cookie).

    The JWT contains claims:
    - sub: user ID (as string)
    - email: user's email address
    - role: role name

    Args:
        credentials: Login request with email and password.
        db: Async database session.

    Returns:
        TokenResponse with access_token and token_type.

    Raises:
        401 INVALID_CREDENTIALS: If email not found or password doesn't match.
        401 ACCOUNT_INACTIVE: If user exists but is deactivated.
    """
    # verify_credentials raises InvalidCredentialsError or AccountInactiveError
    user = await user_service.verify_credentials(db, credentials.email, credentials.password)

    # Create JWT with required claims
    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name,
        }
    )

    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> MeResponse:
    """Get current user's profile, role, and permissions.

    Returns the authenticated user's full profile including:
    - User details (id, email, display_name, etc.)
    - Role details (id, name, description, is_system)
    - List of permission codes the user has

    The user is extracted from the JWT in the Authorization header.

    Args:
        current_user: The authenticated user from JWT.

    Returns:
        MeResponse with user, role, and permissions list.
    """
    # Extract permission codes from the user's role
    permission_codes = [
        rp.permission.code for rp in current_user.role.role_permissions
    ]

    return MeResponse(
        user=UserResponse.model_validate(current_user),
        role=RoleResponse.model_validate(current_user.role),
        permissions=permission_codes,
    )
