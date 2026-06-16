"""Integration tests for authentication flow."""

from datetime import timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.jwt import create_access_token
from app.core.security.passwords import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def auth_test_client() -> AsyncClient:
    """Create a test client with seeded user for authentication tests."""
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
        permission = Permission(
            code="accounts:read",
            module="accounts",
            action="read",
            description="Read accounts",
        )
        session.add(permission)
        await session.flush()

        admin_role = Role(
            id=1, name="Admin", description="Full system access", is_system=True
        )
        session.add(admin_role)
        await session.flush()

        session.add(RolePermission(role_id=admin_role.id, permission_id=permission.id))

        active_user = User(
            id=1,
            email="active@test.com",
            hashed_password=hash_password("correctpassword"),
            display_name="Active User",
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(active_user)

        inactive_user = User(
            id=2,
            email="inactive@test.com",
            hashed_password=hash_password("correctpassword"),
            display_name="Inactive User",
            role_id=admin_role.id,
            is_active=False,
        )
        session.add(inactive_user)

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
async def test_login_success_returns_token(auth_test_client: AsyncClient) -> None:
    """POST /auth/login with valid credentials returns JWT token wrapped in envelope."""
    response = await auth_test_client.post(
        "/auth/login",
        json={"email": "active@test.com", "password": "correctpassword"},
    )

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert "access_token" in envelope["data"]
    assert envelope["data"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password_returns_401(auth_test_client: AsyncClient) -> None:
    """POST /auth/login with wrong password returns 401 INVALID_CREDENTIALS."""
    response = await auth_test_client.post(
        "/auth/login",
        json={"email": "active@test.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(auth_test_client: AsyncClient) -> None:
    """POST /auth/login with unknown email returns 401 INVALID_CREDENTIALS."""
    response = await auth_test_client.post(
        "/auth/login",
        json={"email": "unknown@test.com", "password": "anypassword"},
    )

    assert response.status_code == 401
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_inactive_user_returns_401_account_inactive(
    auth_test_client: AsyncClient,
) -> None:
    """POST /auth/login for deactivated user returns 401 ACCOUNT_INACTIVE."""
    response = await auth_test_client.post(
        "/auth/login",
        json={"email": "inactive@test.com", "password": "correctpassword"},
    )

    assert response.status_code == 401
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "ACCOUNT_INACTIVE"


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(
    auth_test_client: AsyncClient,
) -> None:
    """GET /auth/me with valid token returns user info."""
    login_response = await auth_test_client.post(
        "/auth/login",
        json={"email": "active@test.com", "password": "correctpassword"},
    )
    token = login_response.json()["data"]["access_token"]

    me_response = await auth_test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    envelope = me_response.json()
    assert envelope["success"] is True
    assert envelope["data"]["user"]["email"] == "active@test.com"
    assert envelope["data"]["role"]["name"] == "Admin"
    assert "permissions" in envelope["data"]


@pytest.mark.asyncio
async def test_protected_endpoint_without_token_returns_401(
    auth_test_client: AsyncClient,
) -> None:
    """GET /auth/me without token returns 401."""
    response = await auth_test_client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token_returns_401(
    auth_test_client: AsyncClient,
) -> None:
    """GET /auth/me with invalid token returns 401."""
    response = await auth_test_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    # HTTPException returns detail directly, not wrapped in envelope
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_protected_endpoint_with_expired_token_returns_401(
    auth_test_client: AsyncClient,
) -> None:
    """GET /auth/me with expired token returns 401."""
    expired_token = create_access_token(
        data={"sub": "1"},
        expires_delta=timedelta(seconds=-1),
    )

    response = await auth_test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    # HTTPException returns detail directly, not wrapped in envelope
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_full_auth_flow_login_then_protected_then_without_token(
    auth_test_client: AsyncClient,
) -> None:
    """Integration test: login -> protected call -> call without token returns 401."""
    login_response = await auth_test_client.post(
        "/auth/login",
        json={"email": "active@test.com", "password": "correctpassword"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    me_with_token = await auth_test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_with_token.status_code == 200
    assert me_with_token.json()["data"]["user"]["email"] == "active@test.com"

    me_without_token = await auth_test_client.get("/auth/me")
    assert me_without_token.status_code == 401
