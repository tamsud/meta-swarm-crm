"""Tests for the permissions router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.jwt import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def seeded_client() -> AsyncClient:
    """Create a test client with seeded permissions and an authenticated admin user."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        # Seed permissions
        permissions_data = [
            ("accounts:create", "accounts", "create", "Create accounts"),
            ("accounts:read", "accounts", "read", "Read accounts"),
            ("leads:manage-own", "leads", "manage-own", "Manage own leads"),
            ("leads:manage-all", "leads", "manage-all", "Manage all leads"),
            ("permissions:read", "permissions", "read", "Read permissions"),
        ]
        perm_objects = []
        for code, module, action, desc in permissions_data:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_objects.append(p)
        await session.flush()

        # Create Admin role with all permissions
        admin_role = Role(
            id=1, name="Admin", description="Full system access", is_system=True
        )
        session.add(admin_role)
        await session.flush()

        for p in perm_objects:
            session.add(RolePermission(role_id=admin_role.id, permission_id=p.id))

        # Create admin user
        admin_user = User(
            id=1,
            email="admin@test.com",
            hashed_password="hashed_password",
            display_name="Admin User",
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin_user)
        await session.commit()

    async def override_get_db() -> AsyncSession:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Generate auth token for admin user
    token = create_access_token({"sub": "1"})

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_get_permissions_returns_catalogue(seeded_client: AsyncClient) -> None:
    """GET /permissions returns the full catalogue wrapped in envelope with meta."""
    response = await seeded_client.get("/permissions")

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    data = envelope["data"]
    assert len(data) == 5
    codes = {p["code"] for p in data}
    assert codes == {
        "accounts:create",
        "accounts:read",
        "leads:manage-own",
        "leads:manage-all",
        "permissions:read",
    }
    assert "meta" in envelope
    assert envelope["meta"]["count"] == 5
    assert envelope["meta"]["total"] == 5


@pytest.mark.asyncio
async def test_get_permissions_with_module_filter(seeded_client: AsyncClient) -> None:
    """GET /permissions?module=leads returns only leads permissions."""
    response = await seeded_client.get("/permissions", params={"module": "leads"})

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    data = envelope["data"]
    assert len(data) == 2
    codes = {p["code"] for p in data}
    assert codes == {"leads:manage-own", "leads:manage-all"}
    assert envelope["meta"]["count"] == 2
    assert envelope["meta"]["total"] == 2


@pytest.mark.asyncio
async def test_get_permissions_with_unknown_module_returns_empty(
    seeded_client: AsyncClient,
) -> None:
    """GET /permissions?module=nonexistent returns empty list in envelope with meta."""
    response = await seeded_client.get("/permissions", params={"module": "nonexistent"})

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert envelope["data"] == []
    assert envelope["meta"]["count"] == 0
    assert envelope["meta"]["total"] == 0


def test_no_post_patch_delete_endpoints_for_permissions() -> None:
    """Route-table inspection: no POST/PATCH/DELETE handlers for /permissions."""
    forbidden_methods = {"POST", "PATCH", "DELETE", "PUT"}

    for route in app.routes:
        if hasattr(route, "path") and route.path == "/permissions":
            if hasattr(route, "methods"):
                route_methods = set(route.methods)
                overlap = route_methods & forbidden_methods
                assert not overlap, (
                    f"/permissions route has forbidden methods: {overlap}"
                )
