"""Tests for the permission service."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.services import permission_service


@pytest_asyncio.fixture
async def seeded_permissions(test_db: AsyncSession) -> list[Permission]:
    """Seed test permissions for testing."""
    permissions_data = [
        ("accounts:create", "accounts", "create", "Create accounts"),
        ("accounts:read", "accounts", "read", "Read accounts"),
        ("leads:manage-own", "leads", "manage-own", "Manage own leads"),
        ("leads:manage-all", "leads", "manage-all", "Manage all leads"),
        ("users:manage", "users", "manage", "Manage users"),
    ]

    permissions = []
    for code, module, action, desc in permissions_data:
        perm = Permission(code=code, module=module, action=action, description=desc)
        test_db.add(perm)
        permissions.append(perm)

    await test_db.commit()
    for p in permissions:
        await test_db.refresh(p)

    return permissions


@pytest.mark.asyncio
async def test_list_permissions_returns_all(
    test_db: AsyncSession,
    seeded_permissions: list[Permission],
) -> None:
    """list_permissions() with no filter returns all permissions."""
    result = await permission_service.list_permissions(test_db)

    assert len(result) == 5
    codes = {p.code for p in result}
    assert codes == {
        "accounts:create",
        "accounts:read",
        "leads:manage-own",
        "leads:manage-all",
        "users:manage",
    }


@pytest.mark.asyncio
async def test_list_permissions_filtered_by_module(
    test_db: AsyncSession,
    seeded_permissions: list[Permission],
) -> None:
    """list_permissions(module='leads') returns only leads permissions."""
    result = await permission_service.list_permissions(test_db, module="leads")

    assert len(result) == 2
    codes = {p.code for p in result}
    assert codes == {"leads:manage-own", "leads:manage-all"}


@pytest.mark.asyncio
async def test_list_permissions_empty_module_returns_empty(
    test_db: AsyncSession,
    seeded_permissions: list[Permission],
) -> None:
    """list_permissions(module='nonexistent') returns empty list."""
    result = await permission_service.list_permissions(test_db, module="nonexistent")

    assert result == []


@pytest.mark.asyncio
async def test_list_permissions_ordered_by_module_then_action(
    test_db: AsyncSession,
    seeded_permissions: list[Permission],
) -> None:
    """Permissions are ordered by module, then action."""
    result = await permission_service.list_permissions(test_db)

    codes = [p.code for p in result]
    # Expected order: accounts (create, read), leads (manage-all, manage-own), users (manage)
    assert codes == [
        "accounts:create",
        "accounts:read",
        "leads:manage-all",
        "leads:manage-own",
        "users:manage",
    ]
