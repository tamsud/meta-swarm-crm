"""Tests for the response envelope middleware."""

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
    """Create a test client with seeded permissions, roles, and an authenticated admin user."""
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
        # Seed permissions needed for tests
        permissions_data = [
            ("test:read", "test", "read", "Test permission"),
            ("roles:read", "roles", "read", "Read roles"),
            ("roles:manage", "roles", "manage", "Manage roles"),
            ("permissions:read", "permissions", "read", "Read permissions"),
        ]
        perm_objects = []
        for code, module, action, desc in permissions_data:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_objects.append(p)
        await session.flush()

        # Create Admin role with all permissions
        role = Role(id=1, name="Admin", description="Admin role", is_system=True)
        session.add(role)
        await session.flush()

        for p in perm_objects:
            session.add(RolePermission(role_id=role.id, permission_id=p.id))

        # Create admin user
        admin_user = User(
            id=1,
            email="admin@test.com",
            hashed_password="hashed_password",
            display_name="Admin User",
            role_id=role.id,
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
async def test_success_single_response_envelope(seeded_client: AsyncClient) -> None:
    """Successful GET single resource returns envelope with success=true and data."""
    response = await seeded_client.get("/roles/1")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == "Admin"


@pytest.mark.asyncio
async def test_success_list_response_envelope(seeded_client: AsyncClient) -> None:
    """Successful GET list returns envelope with success=true, data array, and meta."""
    response = await seeded_client.get("/roles")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 1
    assert "meta" in data
    assert data["meta"]["count"] == 1
    assert data["meta"]["total"] == 1
    assert data["meta"]["offset"] == 0
    assert "limit" in data["meta"]


@pytest.mark.asyncio
async def test_app_exception_returns_error_envelope(seeded_client: AsyncClient) -> None:
    """AppException returns envelope with success=false and error details."""
    response = await seeded_client.patch("/roles/1", json={"name": "New Name"})

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "SYSTEM_ROLE_IMMUTABLE"
    assert "message" in data["error"]


@pytest.mark.asyncio
async def test_validation_error_returns_error_envelope(seeded_client: AsyncClient) -> None:
    """Validation error returns 422 with VALIDATION_ERROR code."""
    response = await seeded_client.post("/roles", json={})

    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]


@pytest.mark.asyncio
async def test_empty_list_returns_envelope_with_empty_data_and_meta(
    seeded_client: AsyncClient,
) -> None:
    """Empty list returns envelope with data=[] and meta with count=0."""
    response = await seeded_client.get("/permissions", params={"module": "nonexistent"})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"] == []
    assert "meta" in data
    assert data["meta"]["count"] == 0
    assert data["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_not_found_returns_error_envelope(seeded_client: AsyncClient) -> None:
    """404 error returns envelope with error code."""
    response = await seeded_client.get("/roles/9999")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "ROLE_NOT_FOUND"


@pytest.mark.asyncio
async def test_health_endpoint_not_wrapped(seeded_client: AsyncClient) -> None:
    """/health endpoint is NOT wrapped in envelope."""
    response = await seeded_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "success" not in data
    assert "status" in data


@pytest.mark.asyncio
async def test_create_returns_envelope_with_201(seeded_client: AsyncClient) -> None:
    """POST create returns 201 with envelope."""
    response = await seeded_client.post(
        "/roles",
        json={"name": "Test Role", "permission_ids": []},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Role"


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500_internal_error() -> None:
    """Unhandled exception returns 500 with INTERNAL_ERROR code."""
    from fastapi import FastAPI
    from app.middleware.response_envelope import ResponseEnvelopeMiddleware

    test_app = FastAPI()
    test_app.add_middleware(ResponseEnvelopeMiddleware)

    @test_app.get("/trigger-error")
    async def trigger_error() -> dict:
        raise RuntimeError("Simulated unhandled error")

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/trigger-error")

    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert "message" in data["error"]
