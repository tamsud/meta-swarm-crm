"""Application-level exceptions for service layer errors."""

from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    status_code: int = 400
    error_code: str = "APP_ERROR"
    detail: str = "An error occurred"

    def __init__(
        self,
        detail: str | None = None,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = extra or {}
        super().__init__(self.detail)


class SystemRoleImmutableError(AppException):
    """Raised when attempting to modify or delete a system role."""

    status_code = 400
    error_code = "SYSTEM_ROLE_IMMUTABLE"
    detail = "System roles cannot be modified or deleted"


class RoleHasUsersError(AppException):
    """Raised when attempting to delete a role that has assigned users."""

    status_code = 409
    error_code = "ROLE_HAS_USERS"
    detail = "Cannot delete role with assigned users"

    def __init__(self, user_count: int) -> None:
        super().__init__(
            f"Cannot delete role with {user_count} assigned user(s)",
            extra={"user_count": user_count},
        )


class InvalidPermissionIdsError(AppException):
    """Raised when permission_ids contains non-existent IDs."""

    status_code = 400
    error_code = "INVALID_PERMISSION_IDS"
    detail = "One or more permission IDs are invalid"

    def __init__(self, invalid_ids: list[int]) -> None:
        super().__init__(
            f"Invalid permission IDs: {invalid_ids}",
            extra={"invalid_ids": invalid_ids},
        )


class RoleNotFoundError(AppException):
    """Raised when a role is not found."""

    status_code = 404
    error_code = "ROLE_NOT_FOUND"
    detail = "Role not found"


class DuplicateRoleNameError(AppException):
    """Raised when creating/updating a role with a name that already exists."""

    status_code = 400
    error_code = "DUPLICATE_ROLE_NAME"
    detail = "A role with this name already exists"
