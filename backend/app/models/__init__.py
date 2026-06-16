"""Models package."""

from app.models.permission import Permission
from app.models.role import Role, RolePermission

__all__ = ["Permission", "Role", "RolePermission"]
