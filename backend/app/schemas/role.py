"""Role schemas for request/response validation."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.permission import PermissionResponse


class RoleCreate(BaseModel):
    """Schema for creating a new role."""

    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=256)
    permission_ids: list[int] = Field(..., min_length=0)


class RoleUpdate(BaseModel):
    """Schema for updating an existing role."""

    name: str | None = Field(default=None, min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=256)
    permission_ids: list[int] | None = Field(default=None)


class RoleResponse(BaseModel):
    """Schema for role responses including nested permissions."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionResponse] = []
    permission_count: int = 0
    user_count: int = 0


class RoleListResponse(BaseModel):
    """Schema for paginated role list responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_system: bool
    permission_count: int = 0
    user_count: int = 0
