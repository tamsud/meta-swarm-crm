"""Schemas package."""

from app.schemas.permission import PermissionResponse
from app.schemas.response import (
    ApiError,
    ApiResponse,
    ErrorResponse,
    PaginatedMeta,
    PaginatedResponse,
)
from app.schemas.role import RoleCreate, RoleListResponse, RoleResponse, RoleUpdate
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserResponse,
    UserSelfUpdate,
    UserUpdate,
)

__all__ = [
    "ApiError",
    "ApiResponse",
    "ErrorResponse",
    "PaginatedMeta",
    "PaginatedResponse",
    "PermissionResponse",
    "RoleCreate",
    "RoleListResponse",
    "RoleResponse",
    "RoleUpdate",
    "UserCreate",
    "UserListResponse",
    "UserResponse",
    "UserSelfUpdate",
    "UserUpdate",
]
