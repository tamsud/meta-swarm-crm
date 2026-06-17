"""Integration tests for Mock Email API.

Tests cover:
- CRUD round trip: create -> list -> get (marks read) -> clear -> list (empty)
- Sorting by subject ascending/descending
- Sorting by date ascending/descending
- Search filtering
- 404 for non-existent ID
- 401 for unauthorized request
- 403 for user without mock-email:view permission
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.jwt import create_access_token
from app.core.security.passwords import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.mock_email import MockEmail
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def mock_email_test_client() -> AsyncClient:
    """Create a test client with seeded user and mock-email:view permission."""
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
        # Create mock-email:view permission
        permission = Permission(
            code="mock-email:view",
            module="mock-email",
            action="view",
            description="View mock email inbox",
        )
        session.add(permission)
        await session.flush()

        # Create Admin role with permission
        admin_role = Role(
            id=1, name="Admin", description="Full system access", is_system=True
        )
        session.add(admin_role)
        await session.flush()

        session.add(RolePermission(role_id=admin_role.id, permission_id=permission.id))

        # Create test user
        test_user = User(
            id=1,
            email="admin@test.com",
            hashed_password=hash_password("password123"),
            display_name="Admin User",
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(test_user)
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


@pytest_asyncio.fixture
async def mock_email_no_permission_client() -> AsyncClient:
    """Create a test client with user that lacks mock-email:view permission."""
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
        # Create a role without mock-email:view permission
        limited_role = Role(
            id=1, name="Limited", description="Limited access", is_system=True
        )
        session.add(limited_role)
        await session.flush()

        # Create test user with limited role
        test_user = User(
            id=1,
            email="limited@test.com",
            hashed_password=hash_password("password123"),
            display_name="Limited User",
            role_id=limited_role.id,
            is_active=True,
        )
        session.add(test_user)
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


def get_auth_header(user_id: int = 1) -> dict:
    """Generate Authorization header with valid JWT."""
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Test: CRUD round trip
# ============================================================================


@pytest.mark.asyncio
async def test_crud_round_trip(mock_email_test_client: AsyncClient) -> None:
    """Test full CRUD lifecycle: create -> list -> get (marks read) -> clear -> list (empty)."""
    headers = get_auth_header()

    # Step 1: Create a mock email
    create_response = await mock_email_test_client.post(
        "/mock-emails",
        json={
            "to_email": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email body.",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    envelope = create_response.json()
    assert envelope["success"] is True
    email_data = envelope["data"]
    assert email_data["subject"] == "Test Email"
    assert email_data["to_email"] == "recipient@example.com"
    assert email_data["from_email"] == "crm@demo.local"
    assert email_data["status"] == "unread"
    email_id = email_data["id"]

    # Step 2: List mock emails (should contain our email)
    list_response = await mock_email_test_client.get(
        "/mock-emails",
        headers=headers,
    )
    assert list_response.status_code == 200
    list_envelope = list_response.json()
    assert list_envelope["success"] is True
    assert list_envelope["meta"]["total"] == 1
    assert len(list_envelope["data"]) == 1
    assert list_envelope["data"][0]["subject"] == "Test Email"

    # Step 3: Get the email (marks as read)
    get_response = await mock_email_test_client.get(
        f"/mock-emails/{email_id}",
        headers=headers,
    )
    assert get_response.status_code == 200
    get_envelope = get_response.json()
    assert get_envelope["success"] is True
    assert get_envelope["data"]["status"] == "read"  # Now marked as read

    # Step 4: Clear all emails
    clear_response = await mock_email_test_client.delete(
        "/mock-emails",
        headers=headers,
    )
    assert clear_response.status_code == 200
    clear_envelope = clear_response.json()
    assert clear_envelope["success"] is True
    assert clear_envelope["data"]["deleted_count"] == 1

    # Step 5: List should be empty
    list_after_clear = await mock_email_test_client.get(
        "/mock-emails",
        headers=headers,
    )
    assert list_after_clear.status_code == 200
    assert list_after_clear.json()["meta"]["total"] == 0


# ============================================================================
# Test: Sorting
# ============================================================================


@pytest.mark.asyncio
async def test_sort_by_subject_ascending(mock_email_test_client: AsyncClient) -> None:
    """Test sorting by subject ascending returns alphabetical order."""
    headers = get_auth_header()

    # Create emails with different subjects
    subjects = ["Zebra Email", "Apple Email", "Mango Email"]
    for subject in subjects:
        await mock_email_test_client.post(
            "/mock-emails",
            json={"to_email": "test@example.com", "subject": subject},
            headers=headers,
        )

    response = await mock_email_test_client.get(
        "/mock-emails?sort=subject",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert [e["subject"] for e in data] == ["Apple Email", "Mango Email", "Zebra Email"]


@pytest.mark.asyncio
async def test_sort_by_subject_descending(mock_email_test_client: AsyncClient) -> None:
    """Test sorting by subject descending returns reverse alphabetical order."""
    headers = get_auth_header()

    # Create emails with different subjects
    subjects = ["Zebra Email", "Apple Email", "Mango Email"]
    for subject in subjects:
        await mock_email_test_client.post(
            "/mock-emails",
            json={"to_email": "test@example.com", "subject": subject},
            headers=headers,
        )

    response = await mock_email_test_client.get(
        "/mock-emails?sort=-subject",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert [e["subject"] for e in data] == ["Zebra Email", "Mango Email", "Apple Email"]


@pytest.mark.asyncio
async def test_sort_by_date_ascending(mock_email_test_client: AsyncClient) -> None:
    """Test sorting by date ascending returns oldest first."""
    headers = get_auth_header()

    # Create emails (order created will determine date order)
    for i in range(3):
        await mock_email_test_client.post(
            "/mock-emails",
            json={"to_email": "test@example.com", "subject": f"Email {i}"},
            headers=headers,
        )

    response = await mock_email_test_client.get(
        "/mock-emails?sort=date",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # First created should be first
    assert data[0]["subject"] == "Email 0"
    assert data[1]["subject"] == "Email 1"
    assert data[2]["subject"] == "Email 2"


@pytest.mark.asyncio
async def test_sort_by_date_descending(mock_email_test_client: AsyncClient) -> None:
    """Test sorting by date descending returns newest first."""
    headers = get_auth_header()

    # Create emails (order created will determine date order)
    for i in range(3):
        await mock_email_test_client.post(
            "/mock-emails",
            json={"to_email": "test@example.com", "subject": f"Email {i}"},
            headers=headers,
        )

    response = await mock_email_test_client.get(
        "/mock-emails?sort=-date",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # Last created should be first
    assert data[0]["subject"] == "Email 2"
    assert data[1]["subject"] == "Email 1"
    assert data[2]["subject"] == "Email 0"


# ============================================================================
# Test: Search
# ============================================================================


@pytest.mark.asyncio
async def test_search_filters_to_matching_subjects(
    mock_email_test_client: AsyncClient,
) -> None:
    """Test search filters to only emails with matching subjects."""
    headers = get_auth_header()

    # Create various emails
    await mock_email_test_client.post(
        "/mock-emails",
        json={"to_email": "a@example.com", "subject": "Welcome to CRM"},
        headers=headers,
    )
    await mock_email_test_client.post(
        "/mock-emails",
        json={"to_email": "b@example.com", "subject": "Your Proposal is Ready"},
        headers=headers,
    )
    await mock_email_test_client.post(
        "/mock-emails",
        json={"to_email": "c@example.com", "subject": "Welcome Back"},
        headers=headers,
    )

    # Search for "welcome"
    response = await mock_email_test_client.get(
        "/mock-emails?search=welcome",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    subjects = [e["subject"] for e in data]
    assert "Welcome to CRM" in subjects
    assert "Welcome Back" in subjects
    assert "Your Proposal is Ready" not in subjects


# ============================================================================
# Test: 404 for non-existent ID
# ============================================================================


@pytest.mark.asyncio
async def test_get_nonexistent_id_returns_404(
    mock_email_test_client: AsyncClient,
) -> None:
    """Test GET /mock-emails/{id} with non-existent ID returns 404."""
    headers = get_auth_header()

    response = await mock_email_test_client.get(
        "/mock-emails/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "MOCK_EMAIL_NOT_FOUND"


# ============================================================================
# Test: 401 for unauthorized request
# ============================================================================


@pytest.mark.asyncio
async def test_unauthorized_request_returns_401(
    mock_email_test_client: AsyncClient,
) -> None:
    """Test request without Authorization header returns 401."""
    response = await mock_email_test_client.get("/mock-emails")
    assert response.status_code == 401


# ============================================================================
# Test: 403 for user without permission
# ============================================================================


@pytest.mark.asyncio
async def test_user_without_permission_returns_403(
    mock_email_no_permission_client: AsyncClient,
) -> None:
    """Test user without mock-email:view permission returns 403."""
    headers = get_auth_header()

    response = await mock_email_no_permission_client.get(
        "/mock-emails",
        headers=headers,
    )
    assert response.status_code == 403
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


# ============================================================================
# Test: Mark as read endpoint
# ============================================================================


@pytest.mark.asyncio
async def test_explicit_mark_as_read(mock_email_test_client: AsyncClient) -> None:
    """Test PATCH /mock-emails/{id}/read explicitly marks email as read."""
    headers = get_auth_header()

    # Create an email
    create_response = await mock_email_test_client.post(
        "/mock-emails",
        json={"to_email": "test@example.com", "subject": "Test"},
        headers=headers,
    )
    email_id = create_response.json()["data"]["id"]

    # Mark as read
    response = await mock_email_test_client.patch(
        f"/mock-emails/{email_id}/read",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "read"


@pytest.mark.asyncio
async def test_mark_as_read_nonexistent_returns_404(
    mock_email_test_client: AsyncClient,
) -> None:
    """Test PATCH /mock-emails/{id}/read with non-existent ID returns 404."""
    headers = get_auth_header()

    response = await mock_email_test_client.patch(
        "/mock-emails/00000000-0000-0000-0000-000000000000/read",
        headers=headers,
    )
    assert response.status_code == 404
