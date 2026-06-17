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


# Account exceptions


class AccountNotFoundError(AppException):
    """Raised when an account is not found."""

    status_code = 404
    error_code = "ACCOUNT_NOT_FOUND"
    detail = "Account not found"


class AccountHasDependentsError(AppException):
    """Raised when attempting to delete an account that has associated contacts or opportunities."""

    status_code = 409
    error_code = "ACCOUNT_HAS_DEPENDENTS"
    detail = "Cannot delete account with associated contacts or opportunities"

    def __init__(self, contact_count: int, opportunity_count: int) -> None:
        super().__init__(
            f"Cannot delete account: has {contact_count} contact(s) and {opportunity_count} opportunity(ies)",
            extra={"contact_count": contact_count, "opportunity_count": opportunity_count},
        )


class DuplicateAccountNameError(AppException):
    """Raised when creating/updating an account with a name that already exists."""

    status_code = 409
    error_code = "DUPLICATE_ACCOUNT_NAME"
    detail = "An account with this name already exists"


# User exceptions


class UserNotFoundError(AppException):
    """Raised when a user is not found."""

    status_code = 404
    error_code = "USER_NOT_FOUND"
    detail = "User not found"


class EmailConflictError(AppException):
    """Raised when creating/updating a user with an email that already exists."""

    status_code = 409
    error_code = "EMAIL_CONFLICT"
    detail = "A user with this email already exists"


class LastAdminLockoutError(AppException):
    """Raised when an action would leave zero active Admin users."""

    status_code = 400
    error_code = "LAST_ADMIN_LOCKOUT"
    detail = "Cannot perform this action: at least one active Admin must exist"


class AccountInactiveError(AppException):
    """Raised when an inactive user attempts to authenticate."""

    status_code = 401
    error_code = "ACCOUNT_INACTIVE"
    detail = "This account has been deactivated"


class InvalidCredentialsError(AppException):
    """Raised when login credentials are invalid."""

    status_code = 401
    error_code = "INVALID_CREDENTIALS"
    detail = "Invalid email or password"


class InvalidRoleIdError(AppException):
    """Raised when a role_id does not exist."""

    status_code = 422
    error_code = "INVALID_ROLE_ID"
    detail = "The specified role does not exist"

    def __init__(self, role_id: int) -> None:
        super().__init__(
            f"Role with ID {role_id} does not exist",
            extra={"role_id": role_id},
        )


# JWT / Authentication exceptions


class TokenExpiredError(AppException):
    """Raised when a JWT token has expired."""

    status_code = 401
    error_code = "TOKEN_EXPIRED"
    detail = "Token has expired"


class InvalidTokenError(AppException):
    """Raised when a JWT token is malformed or has an invalid signature."""

    status_code = 401
    error_code = "INVALID_TOKEN"
    detail = "Invalid token"


class InsufficientPermissionsError(AppException):
    """Raised when user lacks a required permission."""

    status_code = 403
    error_code = "INSUFFICIENT_PERMISSIONS"
    detail = "You do not have permission to perform this action"

    def __init__(self, permission_code: str | None = None) -> None:
        if permission_code:
            super().__init__(
                f"Missing required permission: {permission_code}",
                extra={"required_permission": permission_code},
            )
        else:
            super().__init__()


# Contact exceptions


class ContactNotFoundError(AppException):
    """Raised when a contact is not found."""

    status_code = 404
    error_code = "CONTACT_NOT_FOUND"
    detail = "Contact not found"


class ContactEmailConflictError(AppException):
    """Raised when creating/updating a contact with an email that already exists."""

    status_code = 409
    error_code = "EMAIL_CONFLICT"
    detail = "A contact with this email already exists"


class InvalidAccountIdError(AppException):
    """Raised when an account_id does not exist."""

    status_code = 422
    error_code = "INVALID_ACCOUNT_ID"
    detail = "The specified account does not exist"

    def __init__(self, account_id: int) -> None:
        super().__init__(
            f"Account with ID {account_id} does not exist",
            extra={"account_id": account_id},
        )


class InvalidContactIdError(AppException):
    """Raised when a contact_id does not exist."""

    status_code = 422
    error_code = "INVALID_CONTACT_ID"
    detail = "The specified contact does not exist"

    def __init__(self, contact_id: int) -> None:
        super().__init__(
            f"Contact with ID {contact_id} does not exist",
            extra={"contact_id": contact_id},
        )


# Opportunity exceptions


class OpportunityNotFoundError(AppException):
    """Raised when an opportunity is not found."""

    status_code = 404
    error_code = "OPPORTUNITY_NOT_FOUND"
    detail = "Opportunity not found"


# Mock Email exceptions


class MockEmailNotFoundError(AppException):
    """Raised when a mock email is not found."""

    status_code = 404
    error_code = "MOCK_EMAIL_NOT_FOUND"
    detail = "Mock email not found"
