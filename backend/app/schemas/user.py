"""User schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.role import RoleResponse


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    role_id: int = Field(..., description="ID of the role to assign")
    display_name: str | None = Field(default=None, max_length=128, description="Display name")


class UserUpdate(BaseModel):
    """Schema for admin updating an existing user."""

    model_config = ConfigDict(extra="forbid")

    role_id: int | None = Field(default=None, description="ID of the role to assign")
    is_active: bool | None = Field(default=None, description="Whether the user is active")
    display_name: str | None = Field(default=None, max_length=128, description="Display name")


class UserSelfUpdate(BaseModel):
    """Schema for user updating their own profile (limited fields)."""

    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=128, description="Display name")


class UserResponse(BaseModel):
    """Schema for user responses - excludes sensitive fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str | None
    role_id: int
    role: RoleResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Schema for paginated user list responses - excludes nested role details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str | None
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
