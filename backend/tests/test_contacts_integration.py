"""Integration tests for the contacts router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.jwt import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.account import Account
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def seeded_client() -> AsyncClient:
    """Create a test client with seeded permissions, system roles, an admin user, and an account."""
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
            ("accounts:update", "accounts", "update", "Update accounts"),
            ("accounts:delete", "accounts", "delete", "Delete accounts"),
            ("contacts:create", "contacts", "create", "Create contacts"),
            ("contacts:read", "contacts", "read", "Read contacts"),
            ("contacts:update", "contacts", "update", "Update contacts"),
            ("contacts:delete", "contacts", "delete", "Delete contacts"),
        ]
        perm_objects = []
        for code, module, action, desc in permissions_data:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_objects.append(p)
        await session.flush()

        # Create admin role with all permissions
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

        # Create a test account for linking contacts
        test_account = Account(
            id=1,
            name="Test Account",
            industry="Technology",
        )
        session.add(test_account)

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
async def test_crud_round_trip(seeded_client: AsyncClient) -> None:
    """CRUD round-trip: create contact, read it, verify fields match."""
    # Create contact
    create_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "job_title": "Software Engineer",
        },
    )
    assert create_response.status_code == 201
    envelope = create_response.json()
    assert envelope["success"] is True
    contact = envelope["data"]
    contact_id = contact["id"]
    assert contact["first_name"] == "John"
    assert contact["last_name"] == "Doe"
    assert contact["email"] == "john.doe@example.com"
    assert contact["phone"] == "+1-555-123-4567"
    assert contact["job_title"] == "Software Engineer"
    assert contact["account_id"] is None

    # Read contact
    get_response = await seeded_client.get(f"/contacts/{contact_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()["data"]
    assert fetched["first_name"] == "John"
    assert fetched["last_name"] == "Doe"
    assert fetched["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_crud_with_account_id(seeded_client: AsyncClient) -> None:
    """Create contact linked to account, verify account_id persisted."""
    create_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "account_id": 1,
        },
    )
    assert create_response.status_code == 201
    contact = create_response.json()["data"]
    assert contact["account_id"] == 1
    assert contact["account"]["name"] == "Test Account"


@pytest.mark.asyncio
async def test_crud_without_account_id(seeded_client: AsyncClient) -> None:
    """Create contact with null account, verify works."""
    create_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Bob",
            "last_name": "Wilson",
            "email": "bob.wilson@example.com",
        },
    )
    assert create_response.status_code == 201
    contact = create_response.json()["data"]
    assert contact["account_id"] is None
    assert contact["account"] is None


@pytest.mark.asyncio
async def test_duplicate_email_on_create_returns_409(seeded_client: AsyncClient) -> None:
    """Duplicate email on create returns 409 EMAIL_CONFLICT."""
    # Create first contact
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "First",
            "last_name": "Contact",
            "email": "duplicate@example.com",
        },
    )

    # Try to create second contact with same email
    response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Second",
            "last_name": "Contact",
            "email": "duplicate@example.com",
        },
    )
    assert response.status_code == 409
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "EMAIL_CONFLICT"


@pytest.mark.asyncio
async def test_duplicate_email_on_update_returns_409(seeded_client: AsyncClient) -> None:
    """Duplicate email on update returns 409 EMAIL_CONFLICT."""
    # Create two contacts
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "First",
            "last_name": "Contact",
            "email": "first@example.com",
        },
    )

    second_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Second",
            "last_name": "Contact",
            "email": "second@example.com",
        },
    )
    second_id = second_response.json()["data"]["id"]

    # Try to update second contact with first's email
    response = await seeded_client.patch(
        f"/contacts/{second_id}",
        json={"email": "first@example.com"},
    )
    assert response.status_code == 409
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "EMAIL_CONFLICT"


@pytest.mark.asyncio
async def test_case_insensitive_email_check(seeded_client: AsyncClient) -> None:
    """Case-insensitive email check: create with 'Test@Example.com', try 'test@example.com' -> 409."""
    # Create contact with mixed-case email
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "Test@Example.com",
        },
    )

    # Try to create with same email in different case
    response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Another",
            "last_name": "User",
            "email": "test@example.com",
        },
    )
    assert response.status_code == 409
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "EMAIL_CONFLICT"


@pytest.mark.asyncio
async def test_invalid_account_id_on_create_returns_422(seeded_client: AsyncClient) -> None:
    """Invalid account_id on create returns 422."""
    response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test.invalid.account@example.com",
            "account_id": 9999,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_ACCOUNT_ID"


@pytest.mark.asyncio
async def test_filter_by_account_id(seeded_client: AsyncClient) -> None:
    """GET /contacts?account_id=X returns only contacts with that account."""
    # Create contacts with different accounts
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "With",
            "last_name": "Account",
            "email": "with.account@example.com",
            "account_id": 1,
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Without",
            "last_name": "Account",
            "email": "without.account@example.com",
        },
    )

    # Filter by account_id
    response = await seeded_client.get("/contacts", params={"account_id": 1})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert all(c["account_id"] == 1 for c in envelope["data"])


@pytest.mark.asyncio
async def test_search_matches_partial_name_and_email(seeded_client: AsyncClient) -> None:
    """GET /contacts?search=partial matches partial first name, last name, and email."""
    # Create contacts with searchable data
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "SearchFirst",
            "last_name": "UserA",
            "email": "usera@search.com",
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "UserB",
            "last_name": "SearchLast",
            "email": "userb@test.com",
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "UserC",
            "last_name": "NoMatch",
            "email": "searchemail@test.com",
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "NoMatch",
            "last_name": "NoMatch",
            "email": "nomatch@test.com",
        },
    )

    # Search for "search" (case-insensitive)
    response = await seeded_client.get("/contacts", params={"search": "search"})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    # Should find SearchFirst, SearchLast, and searchemail
    assert len(envelope["data"]) == 3


@pytest.mark.asyncio
async def test_get_nonexistent_contact_returns_404(seeded_client: AsyncClient) -> None:
    """GET /contacts/{id} for non-existent ID returns 404 CONTACT_NOT_FOUND."""
    response = await seeded_client.get("/contacts/9999")
    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "CONTACT_NOT_FOUND"


@pytest.mark.asyncio
async def test_pagination(seeded_client: AsyncClient) -> None:
    """Pagination: create 5 contacts, request limit=2, verify count/total in meta."""
    # Create 5 contacts
    for i in range(5):
        await seeded_client.post(
            "/contacts",
            json={
                "first_name": f"Pagination{i}",
                "last_name": "User",
                "email": f"pagination{i}@example.com",
            },
        )

    # Request with limit=2
    response = await seeded_client.get("/contacts", params={"offset": 0, "limit": 2})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert len(envelope["data"]) == 2
    assert envelope["meta"]["count"] == 2
    assert envelope["meta"]["total"] == 5
    assert envelope["meta"]["offset"] == 0
    assert envelope["meta"]["limit"] == 2

    # Request second page
    response2 = await seeded_client.get("/contacts", params={"offset": 2, "limit": 2})
    assert response2.status_code == 200
    envelope2 = response2.json()
    assert len(envelope2["data"]) == 2
    assert envelope2["meta"]["count"] == 2
    assert envelope2["meta"]["total"] == 5
    assert envelope2["meta"]["offset"] == 2


@pytest.mark.asyncio
async def test_sorting(seeded_client: AsyncClient) -> None:
    """Sorting: verify sort by first_name ascending/descending returns correct order."""
    # Create contacts with specific names for sorting
    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Zebra",
            "last_name": "User",
            "email": "zebra@example.com",
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Alpha",
            "last_name": "User",
            "email": "alpha@example.com",
        },
    )

    await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Middle",
            "last_name": "User",
            "email": "middle@example.com",
        },
    )

    # Sort ascending
    response_asc = await seeded_client.get("/contacts", params={"sort": "first_name"})
    assert response_asc.status_code == 200
    items_asc = response_asc.json()["data"]
    names_asc = [c["first_name"] for c in items_asc]
    assert names_asc == sorted(names_asc)

    # Sort descending
    response_desc = await seeded_client.get("/contacts", params={"sort": "-first_name"})
    assert response_desc.status_code == 200
    items_desc = response_desc.json()["data"]
    names_desc = [c["first_name"] for c in items_desc]
    assert names_desc == sorted(names_desc, reverse=True)


@pytest.mark.asyncio
async def test_delete_contact_returns_204(seeded_client: AsyncClient) -> None:
    """Delete contact returns 204 and subsequent GET returns 404."""
    # Create contact
    create_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "ToDelete",
            "last_name": "User",
            "email": "todelete@example.com",
        },
    )
    contact_id = create_response.json()["data"]["id"]

    # Delete contact
    delete_response = await seeded_client.delete(f"/contacts/{contact_id}")
    assert delete_response.status_code == 204

    # Verify GET returns 404
    get_response = await seeded_client.get(f"/contacts/{contact_id}")
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "CONTACT_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_contact_success(seeded_client: AsyncClient) -> None:
    """Update contact with valid data succeeds."""
    # Create contact
    create_response = await seeded_client.post(
        "/contacts",
        json={
            "first_name": "Original",
            "last_name": "Name",
            "email": "original@example.com",
        },
    )
    contact_id = create_response.json()["data"]["id"]

    # Update contact
    update_response = await seeded_client.patch(
        f"/contacts/{contact_id}",
        json={
            "first_name": "Updated",
            "job_title": "Manager",
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()["data"]
    assert updated["first_name"] == "Updated"
    assert updated["last_name"] == "Name"  # Unchanged
    assert updated["job_title"] == "Manager"
