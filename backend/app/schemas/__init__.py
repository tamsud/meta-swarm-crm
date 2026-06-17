"""Schemas package."""

from app.schemas.contact import (
    AccountBrief,
    ContactCreate,
    ContactResponse,
    ContactUpdate,
)
from app.schemas.mock_email import (
    MockEmailCreate,
    MockEmailDetail,
    MockEmailListItem,
    MockEmailListResponse,
)
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunityUpdate,
)
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
    "AccountBrief",
    "ApiError",
    "ApiResponse",
    "ContactCreate",
    "ContactResponse",
    "ContactUpdate",
    "ErrorResponse",
    "MockEmailCreate",
    "MockEmailDetail",
    "MockEmailListItem",
    "MockEmailListResponse",
    "OpportunityCreate",
    "OpportunityResponse",
    "OpportunityUpdate",
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
