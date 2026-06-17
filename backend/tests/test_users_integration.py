"""Integration tests for the users router (WU-USR-8)."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.passwords import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def users_client() -> AsyncClient:
    """Test client seeded with 3 demo users across Admin/Manager/Sales Rep roles."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as session:
        perms = [
            ("users:manage", "users", "manage", "Manage users"),
            ("accounts:read", "accounts", "read", "Read accounts"),
        ]
        perm_map: dict[str, Permission] = {}
        for code, module, action, desc in perms:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_map[code] = p
        await session.flush()

        admin_role = Role(id=1, name="Admin", description="Full system access", is_system=True)
        manager_role = Role(id=2, name="Manager", description="Manager access", is_system=True)
        sales_role = Role(id=3, name="Sales Rep", description="Sales access", is_system=True)
        session.add_all([admin_role, manager_role, sales_role])
        await session.flush()

        # Admin gets all permissions; Manager and Sales Rep get read-only
        for p in perm_map.values():
            session.add(RolePermission(role_id=admin_role.id, permission_id=p.id))
        session.add(RolePermission(role_id=manager_role.id, permission_id=perm_map["accounts:read"].id))
        session.add(RolePermission(role_id=sales_role.id, permission_id=perm_map["accounts:read"].id))

        users = [
            User(email="admin@crm.local", hashed_password=hash_password("password123"),
                 display_name="Admin User", role_id=1, is_active=True),
            User(email="manager@crm.local", hashed_password=hash_password("password123"),
                 display_name="Manager User", role_id=2, is_active=True),
            User(email="sales@crm.local", hashed_password=hash_password("password123"),
                 display_name="Sales Rep", role_id=3, is_active=True),
        ]
        session.add_all(users)
        await session.commit()

    async def override_get_db() -> AsyncSession:
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


async def _login(client: AsyncClient, email: str, password: str = "password123") -> str:
    """Return JWT token for the given credentials."""
    resp = await client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["data"]["access_token"]


# ---------------------------------------------------------------------------
# Test: all 3 seed demo users can log in with the correct role
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_seed_users_login_with_correct_role(users_client: AsyncClient) -> None:
    """admin@crm.local → Admin, manager@crm.local → Manager, sales@crm.local → Sales Rep."""
    for email, expected_role in [
        ("admin@crm.local", "Admin"),
        ("manager@crm.local", "Manager"),
        ("sales@crm.local", "Sales Rep"),
    ]:
        token = await _login(users_client, email)
        me_resp = await users_client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200, f"{email} /auth/me failed"
        assert me_resp.json()["data"]["role"]["name"] == expected_role, (
            f"{email} expected role {expected_role}"
        )


# ---------------------------------------------------------------------------
# Test: duplicate email → 409 EMAIL_CONFLICT
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_user_duplicate_email_returns_409(users_client: AsyncClient) -> None:
    """POST /users with an already-used email returns 409 EMAIL_CONFLICT."""
    token = await _login(users_client, "admin@crm.local")
    headers = {"Authorization": f"Bearer {token}"}

    # First create a user so we have a known-good duplicate target
    await users_client.post(
        "/users",
        json={"email": "duplicate@example.com", "password": "password123", "role_id": 2},
        headers=headers,
    )

    # Try to create the same email again
    resp = await users_client.post(
        "/users",
        json={"email": "duplicate@example.com", "password": "password123", "role_id": 2},
        headers=headers,
    )

    assert resp.status_code == 409
    envelope = resp.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "EMAIL_CONFLICT"


# ---------------------------------------------------------------------------
# Test: LAST_ADMIN_LOCKOUT — deactivating the last Admin
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deactivate_last_admin_returns_400(users_client: AsyncClient) -> None:
    """PATCH /users/{id} deactivating the sole active Admin returns 400 LAST_ADMIN_LOCKOUT."""
    token = await _login(users_client, "admin@crm.local")
    headers = {"Authorization": f"Bearer {token}"}

    me_resp = await users_client.get("/auth/me", headers=headers)
    admin_id = me_resp.json()["data"]["user"]["id"]

    resp = await users_client.patch(
        f"/users/{admin_id}", json={"is_active": False}, headers=headers
    )

    assert resp.status_code == 400
    envelope = resp.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "LAST_ADMIN_LOCKOUT"


# ---------------------------------------------------------------------------
# Test: LAST_ADMIN_LOCKOUT — changing the last Admin's role
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_change_last_admin_role_returns_400(users_client: AsyncClient) -> None:
    """PATCH /users/{id} changing the sole Admin's role returns 400 LAST_ADMIN_LOCKOUT."""
    token = await _login(users_client, "admin@crm.local")
    headers = {"Authorization": f"Bearer {token}"}

    me_resp = await users_client.get("/auth/me", headers=headers)
    admin_id = me_resp.json()["data"]["user"]["id"]

    resp = await users_client.patch(
        f"/users/{admin_id}", json={"role_id": 2}, headers=headers  # Admin → Manager
    )

    assert resp.status_code == 400
    envelope = resp.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "LAST_ADMIN_LOCKOUT"


# ---------------------------------------------------------------------------
# Test: non-Admin GET /users returns 403
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_admin_list_users_returns_403(users_client: AsyncClient) -> None:
    """GET /users by a user without users:manage returns 403."""
    token = await _login(users_client, "manager@crm.local")

    resp = await users_client.get("/users", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Test: deactivated user's login → 401 ACCOUNT_INACTIVE
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deactivated_user_login_returns_401(users_client: AsyncClient) -> None:
    """POST /auth/login for a deactivated user returns 401 ACCOUNT_INACTIVE."""
    admin_token = await _login(users_client, "admin@crm.local")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Find and deactivate manager
    list_resp = await users_client.get(
        "/users?search=manager@crm.local", headers=admin_headers
    )
    manager_id = list_resp.json()["data"][0]["id"]
    await users_client.patch(
        f"/users/{manager_id}", json={"is_active": False}, headers=admin_headers
    )

    # Deactivated login attempt
    resp = await users_client.post(
        "/auth/login", json={"email": "manager@crm.local", "password": "password123"}
    )

    assert resp.status_code == 401
    envelope = resp.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "ACCOUNT_INACTIVE"


# ---------------------------------------------------------------------------
# Test: deactivated user's existing token → 401 on protected endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deactivated_user_token_rejected_on_protected_endpoint(
    users_client: AsyncClient,
) -> None:
    """A token issued before deactivation is rejected with 401 on GET /users/me."""
    # Obtain token BEFORE deactivation
    manager_token = await _login(users_client, "manager@crm.local")

    # Admin deactivates manager
    admin_token = await _login(users_client, "admin@crm.local")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    list_resp = await users_client.get(
        "/users?search=manager@crm.local", headers=admin_headers
    )
    manager_id = list_resp.json()["data"][0]["id"]
    await users_client.patch(
        f"/users/{manager_id}", json={"is_active": False}, headers=admin_headers
    )

    # Use the old token — dependency raises HTTPException (not AppException)
    resp = await users_client.get(
        "/auth/me", headers={"Authorization": f"Bearer {manager_token}"}
    )

    assert resp.status_code == 401
    # get_current_user raises HTTPException → response has "detail", not wrapped envelope
    data = resp.json()
    assert "detail" in data


# ---------------------------------------------------------------------------
# Test: PATCH /users/me with extra fields → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_me_extra_fields_returns_422(users_client: AsyncClient) -> None:
    """PATCH /users/me rejects extra fields (e.g., is_active) with 422."""
    token = await _login(users_client, "admin@crm.local")

    resp = await users_client.patch(
        "/users/me",
        json={"display_name": "New Name", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Test: full CRUD round trip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_crud_round_trip(users_client: AsyncClient) -> None:
    """Create → list → get → update display_name → deactivate."""
    token = await _login(users_client, "admin@crm.local")
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    create_resp = await users_client.post(
        "/users",
        json={"email": "newuser@test.com", "password": "password123", "role_id": 2,
              "display_name": "New User"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["data"]["id"]
    assert create_resp.json()["data"]["email"] == "newuser@test.com"

    # List — finds the new user
    list_resp = await users_client.get("/users?search=newuser@test.com", headers=headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["meta"]["total"] == 1

    # Get by ID
    get_resp = await users_client.get(f"/users/{user_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["display_name"] == "New User"

    # Update display_name
    patch_resp = await users_client.patch(
        f"/users/{user_id}", json={"display_name": "Updated Name"}, headers=headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["display_name"] == "Updated Name"

    # Deactivate
    deactivate_resp = await users_client.patch(
        f"/users/{user_id}", json={"is_active": False}, headers=headers
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["data"]["is_active"] is False
