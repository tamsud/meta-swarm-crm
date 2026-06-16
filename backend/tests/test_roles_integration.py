"""Integration tests for the roles router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.permission import Permission
from app.models.role import Role, RolePermission


@pytest_asyncio.fixture
async def seeded_client() -> AsyncClient:
    """Create a test client with seeded permissions and system roles."""
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
        permissions_data = [
            ("accounts:create", "accounts", "create", "Create accounts"),
            ("accounts:read", "accounts", "read", "Read accounts"),
            ("accounts:update", "accounts", "update", "Update accounts"),
            ("contacts:create", "contacts", "create", "Create contacts"),
            ("contacts:read", "contacts", "read", "Read contacts"),
        ]
        perm_objects = []
        for code, module, action, desc in permissions_data:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_objects.append(p)
        await session.flush()

        admin_role = Role(
            id=1, name="Admin", description="Full system access", is_system=True
        )
        session.add(admin_role)
        await session.flush()

        for p in perm_objects:
            session.add(RolePermission(role_id=admin_role.id, permission_id=p.id))

        await session.commit()

    async def override_get_db() -> AsyncSession:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_patch_admin_role_name_returns_400_system_role_immutable(
    seeded_client: AsyncClient,
) -> None:
    """PATCH on Admin role name returns 400 SYSTEM_ROLE_IMMUTABLE."""
    response = await seeded_client.patch(
        "/roles/1",
        json={"name": "Super Admin"},
    )

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "SYSTEM_ROLE_IMMUTABLE"


@pytest.mark.asyncio
async def test_patch_admin_role_permission_ids_returns_400_system_role_immutable(
    seeded_client: AsyncClient,
) -> None:
    """PATCH on Admin role permission_ids returns 400 SYSTEM_ROLE_IMMUTABLE."""
    response = await seeded_client.patch(
        "/roles/1",
        json={"permission_ids": [1, 2]},
    )

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "SYSTEM_ROLE_IMMUTABLE"


@pytest.mark.asyncio
async def test_delete_admin_role_returns_400_system_role_immutable(
    seeded_client: AsyncClient,
) -> None:
    """DELETE on Admin role returns 400 SYSTEM_ROLE_IMMUTABLE."""
    response = await seeded_client.delete("/roles/1")

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "SYSTEM_ROLE_IMMUTABLE"


@pytest.mark.asyncio
async def test_post_roles_with_invalid_permission_id_returns_400(
    seeded_client: AsyncClient,
) -> None:
    """POST /roles with invalid permission_id returns 400."""
    response = await seeded_client.post(
        "/roles",
        json={
            "name": "Test Role",
            "permission_ids": [9999],
        },
    )

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_PERMISSION_IDS"
    assert 9999 in envelope["error"]["invalid_ids"]


@pytest.mark.asyncio
async def test_custom_role_crud_round_trip(seeded_client: AsyncClient) -> None:
    """Custom role CRUD round trip - create, update permissions, verify changes."""
    create_response = await seeded_client.post(
        "/roles",
        json={
            "name": "Sales Team",
            "description": "Sales team role",
            "permission_ids": [1, 2],
        },
    )
    assert create_response.status_code == 201
    envelope = create_response.json()
    assert envelope["success"] is True
    created = envelope["data"]
    role_id = created["id"]
    assert created["name"] == "Sales Team"
    assert created["is_system"] is False
    assert created["permission_count"] == 2

    update_response = await seeded_client.patch(
        f"/roles/{role_id}",
        json={"permission_ids": [1, 2, 3, 4]},
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["permission_count"] == 4

    get_response = await seeded_client.get(f"/roles/{role_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()["data"]
    assert fetched["permission_count"] == 4
    assert len(fetched["permissions"]) == 4

    delete_response = await seeded_client.delete(f"/roles/{role_id}")
    assert delete_response.status_code == 204

    get_after_delete = await seeded_client.get(f"/roles/{role_id}")
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_list_roles_with_pagination(seeded_client: AsyncClient) -> None:
    """GET /roles supports pagination parameters and returns meta."""
    for i in range(5):
        await seeded_client.post(
            "/roles",
            json={"name": f"Role {i}", "permission_ids": []},
        )

    response = await seeded_client.get("/roles", params={"offset": 0, "limit": 3})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert len(envelope["data"]) == 3
    assert envelope["meta"]["count"] == 3
    assert envelope["meta"]["total"] == 6
    assert envelope["meta"]["offset"] == 0
    assert envelope["meta"]["limit"] == 3

    response2 = await seeded_client.get("/roles", params={"offset": 3, "limit": 3})
    assert response2.status_code == 200
    envelope2 = response2.json()
    assert len(envelope2["data"]) == 3
    assert envelope2["meta"]["count"] == 3
    assert envelope2["meta"]["total"] == 6
    assert envelope2["meta"]["offset"] == 3


@pytest.mark.asyncio
async def test_get_nonexistent_role_returns_404(seeded_client: AsyncClient) -> None:
    """GET /roles/{id} with invalid id returns 404."""
    response = await seeded_client.get("/roles/9999")
    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "ROLE_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_role_with_duplicate_name_returns_400(
    seeded_client: AsyncClient,
) -> None:
    """POST /roles with duplicate name returns 400."""
    await seeded_client.post(
        "/roles",
        json={"name": "Duplicate Role", "permission_ids": []},
    )

    response = await seeded_client.post(
        "/roles",
        json={"name": "Duplicate Role", "permission_ids": []},
    )

    assert response.status_code == 400
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "DUPLICATE_ROLE_NAME"
