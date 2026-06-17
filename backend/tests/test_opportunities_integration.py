"""Integration tests for the opportunities router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security.jwt import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.account import Account
from app.models.contact import Contact
from app.models.permission import Permission
from app.models.role import Role, RolePermission
from app.models.user import User


@pytest_asyncio.fixture
async def seeded_client_with_sales_rep() -> tuple[AsyncClient, AsyncClient]:
    """Create test clients with admin and sales rep users (sales rep lacks opportunities:delete)."""
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
            ("opportunities:create", "opportunities", "create", "Create opportunities"),
            ("opportunities:read", "opportunities", "read", "Read opportunities"),
            ("opportunities:update", "opportunities", "update", "Update opportunities"),
            ("opportunities:delete", "opportunities", "delete", "Delete opportunities"),
        ]
        perm_objects = []
        for code, module, action, desc in permissions_data:
            p = Permission(code=code, module=module, action=action, description=desc)
            session.add(p)
            perm_objects.append(p)
        await session.flush()

        # Create admin role with all permissions (including opportunities:delete)
        admin_role = Role(
            id=1, name="Admin", description="Full system access", is_system=True
        )
        session.add(admin_role)
        await session.flush()

        for p in perm_objects:
            session.add(RolePermission(role_id=admin_role.id, permission_id=p.id))

        # Create sales rep role WITHOUT opportunities:delete
        sales_rep_role = Role(
            id=2, name="Sales Rep", description="Sales representative access", is_system=True
        )
        session.add(sales_rep_role)
        await session.flush()

        # Sales rep gets all permissions except opportunities:delete
        for p in perm_objects:
            if p.code != "opportunities:delete":
                session.add(RolePermission(role_id=sales_rep_role.id, permission_id=p.id))

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

        # Create sales rep user
        sales_rep_user = User(
            id=2,
            email="salesrep@test.com",
            hashed_password="hashed_password",
            display_name="Sales Rep User",
            role_id=sales_rep_role.id,
            is_active=True,
        )
        session.add(sales_rep_user)

        # Create a test account for linking opportunities
        test_account = Account(
            id=1,
            name="Test Account",
            industry="Technology",
        )
        session.add(test_account)

        # Create a test contact for optional linking
        test_contact = Contact(
            id=1,
            first_name="Test",
            last_name="Contact",
            email="test.contact@example.com",
            account_id=1,
        )
        session.add(test_contact)

        await session.commit()

    async def override_get_db() -> AsyncSession:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Generate auth tokens
    admin_token = create_access_token({"sub": "1"})
    sales_rep_token = create_access_token({"sub": "2"})

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as admin_client, AsyncClient(
        transport=transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {sales_rep_token}"},
    ) as sales_rep_client:
        yield admin_client, sales_rep_client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest_asyncio.fixture
async def seeded_client() -> AsyncClient:
    """Create a test client with seeded permissions, system roles, an admin user, an account, and a contact."""
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
            ("opportunities:create", "opportunities", "create", "Create opportunities"),
            ("opportunities:read", "opportunities", "read", "Read opportunities"),
            ("opportunities:update", "opportunities", "update", "Update opportunities"),
            ("opportunities:delete", "opportunities", "delete", "Delete opportunities"),
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

        # Create a test account for linking opportunities
        test_account = Account(
            id=1,
            name="Test Account",
            industry="Technology",
        )
        session.add(test_account)

        # Create a test contact for optional linking
        test_contact = Contact(
            id=1,
            first_name="Test",
            last_name="Contact",
            email="test.contact@example.com",
            account_id=1,
        )
        session.add(test_contact)

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
async def test_create_opportunity_without_stage_defaults_to_prospecting(
    seeded_client: AsyncClient,
) -> None:
    """Create opportunity without stage - stage defaults to prospecting."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "New Deal",
            "account_id": 1,
        },
    )
    assert response.status_code == 201
    envelope = response.json()
    assert envelope["success"] is True
    opportunity = envelope["data"]
    assert opportunity["title"] == "New Deal"
    assert opportunity["account_id"] == 1
    assert opportunity["stage"] == "prospecting"


@pytest.mark.asyncio
async def test_create_opportunity_with_value_zero_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create opportunity with value = 0 returns 422 before DB write."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Zero Value Deal",
            "account_id": 1,
            "value": 0,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False


@pytest.mark.asyncio
async def test_create_opportunity_with_value_negative_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create opportunity with value = -1 returns 422."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Negative Value Deal",
            "account_id": 1,
            "value": -1,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False


@pytest.mark.asyncio
async def test_create_opportunity_with_probability_negative_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create opportunity with probability = -1 returns 422."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Invalid Probability Deal",
            "account_id": 1,
            "probability": -1,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False


@pytest.mark.asyncio
async def test_create_opportunity_with_probability_101_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create opportunity with probability = 101 returns 422."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Invalid Probability Deal",
            "account_id": 1,
            "probability": 101,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False


@pytest.mark.asyncio
async def test_patch_stage_from_closed_won_to_prospecting_succeeds(
    seeded_client: AsyncClient,
) -> None:
    """PATCH stage from closed_won to prospecting succeeds (non-linear allowed)."""
    # Create opportunity with closed_won stage
    create_response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Won Deal",
            "account_id": 1,
            "stage": "closed_won",
        },
    )
    assert create_response.status_code == 201
    opportunity_id = create_response.json()["data"]["id"]

    # Patch to prospecting (non-linear transition)
    patch_response = await seeded_client.patch(
        f"/opportunities/{opportunity_id}",
        json={"stage": "prospecting"},
    )
    assert patch_response.status_code == 200
    updated = patch_response.json()["data"]
    assert updated["stage"] == "prospecting"


@pytest.mark.asyncio
async def test_get_opportunities_filter_by_stage(
    seeded_client: AsyncClient,
) -> None:
    """GET /opportunities?stage=proposal returns only matching records."""
    # Create opportunities with different stages
    await seeded_client.post(
        "/opportunities",
        json={"title": "Prospecting Deal", "account_id": 1, "stage": "prospecting"},
    )
    await seeded_client.post(
        "/opportunities",
        json={"title": "Proposal Deal", "account_id": 1, "stage": "proposal"},
    )
    await seeded_client.post(
        "/opportunities",
        json={"title": "Another Proposal Deal", "account_id": 1, "stage": "proposal"},
    )

    # Filter by stage=proposal
    response = await seeded_client.get("/opportunities", params={"stage": "proposal"})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert all(o["stage"] == "proposal" for o in envelope["data"])
    assert len(envelope["data"]) == 2


@pytest.mark.asyncio
async def test_sales_rep_delete_returns_403(
    seeded_client_with_sales_rep: tuple[AsyncClient, AsyncClient],
) -> None:
    """Sales Rep DELETE returns 403."""
    admin_client, sales_rep_client = seeded_client_with_sales_rep

    # Admin creates an opportunity
    create_response = await admin_client.post(
        "/opportunities",
        json={"title": "To Delete", "account_id": 1},
    )
    assert create_response.status_code == 201
    opportunity_id = create_response.json()["data"]["id"]

    # Sales rep tries to delete - should get 403
    delete_response = await sales_rep_client.delete(f"/opportunities/{opportunity_id}")
    assert delete_response.status_code == 403
    envelope = delete_response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INSUFFICIENT_PERMISSIONS"


@pytest.mark.asyncio
async def test_manager_delete_returns_204(
    seeded_client: AsyncClient,
) -> None:
    """Manager/Admin DELETE returns 204."""
    # Create an opportunity
    create_response = await seeded_client.post(
        "/opportunities",
        json={"title": "To Delete", "account_id": 1},
    )
    assert create_response.status_code == 201
    opportunity_id = create_response.json()["data"]["id"]

    # Delete the opportunity
    delete_response = await seeded_client.delete(f"/opportunities/{opportunity_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await seeded_client.get(f"/opportunities/{opportunity_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_with_invalid_account_id_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create with invalid account_id returns 422."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Invalid Account Deal",
            "account_id": 9999,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_ACCOUNT_ID"


@pytest.mark.asyncio
async def test_create_with_invalid_contact_id_returns_422(
    seeded_client: AsyncClient,
) -> None:
    """Create with invalid contact_id returns 422."""
    response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Invalid Contact Deal",
            "account_id": 1,
            "contact_id": 9999,
        },
    )
    assert response.status_code == 422
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "INVALID_CONTACT_ID"


@pytest.mark.asyncio
async def test_get_nonexistent_opportunity_returns_404(
    seeded_client: AsyncClient,
) -> None:
    """GET /opportunities/{id} with non-existent ID returns 404."""
    response = await seeded_client.get("/opportunities/9999")
    assert response.status_code == 404
    envelope = response.json()
    assert envelope["success"] is False
    assert envelope["error"]["code"] == "OPPORTUNITY_NOT_FOUND"


@pytest.mark.asyncio
async def test_crud_round_trip(seeded_client: AsyncClient) -> None:
    """CRUD round-trip: create opportunity, read it, update it, verify fields."""
    # Create opportunity
    create_response = await seeded_client.post(
        "/opportunities",
        json={
            "title": "Big Deal",
            "account_id": 1,
            "contact_id": 1,
            "value": 50000.00,
            "probability": 75,
            "expected_close_date": "2026-12-31",
        },
    )
    assert create_response.status_code == 201
    envelope = create_response.json()
    assert envelope["success"] is True
    opportunity = envelope["data"]
    opportunity_id = opportunity["id"]
    assert opportunity["title"] == "Big Deal"
    assert opportunity["account_id"] == 1
    assert opportunity["contact_id"] == 1
    assert opportunity["stage"] == "prospecting"
    assert float(opportunity["value"]) == 50000.00
    assert opportunity["probability"] == 75
    assert opportunity["expected_close_date"] == "2026-12-31"

    # Read opportunity
    get_response = await seeded_client.get(f"/opportunities/{opportunity_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()["data"]
    assert fetched["title"] == "Big Deal"

    # Update opportunity
    patch_response = await seeded_client.patch(
        f"/opportunities/{opportunity_id}",
        json={
            "title": "Updated Big Deal",
            "stage": "negotiation",
            "probability": 90,
        },
    )
    assert patch_response.status_code == 200
    updated = patch_response.json()["data"]
    assert updated["title"] == "Updated Big Deal"
    assert updated["stage"] == "negotiation"
    assert updated["probability"] == 90
    # Unchanged fields should remain
    assert float(updated["value"]) == 50000.00


@pytest.mark.asyncio
async def test_filter_by_account_id(seeded_client: AsyncClient) -> None:
    """GET /opportunities?account_id=X returns only opportunities for that account."""
    # Create opportunities
    await seeded_client.post(
        "/opportunities",
        json={"title": "Deal for Account 1", "account_id": 1},
    )

    # Filter by account_id
    response = await seeded_client.get("/opportunities", params={"account_id": 1})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert all(o["account_id"] == 1 for o in envelope["data"])


@pytest.mark.asyncio
async def test_pagination(seeded_client: AsyncClient) -> None:
    """Pagination: create 5 opportunities, request limit=2, verify count/total in meta."""
    # Create 5 opportunities
    for i in range(5):
        await seeded_client.post(
            "/opportunities",
            json={"title": f"Deal {i}", "account_id": 1},
        )

    # Request with limit=2
    response = await seeded_client.get("/opportunities", params={"offset": 0, "limit": 2})
    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert len(envelope["data"]) == 2
    assert envelope["meta"]["count"] == 2
    assert envelope["meta"]["total"] == 5
    assert envelope["meta"]["offset"] == 0
    assert envelope["meta"]["limit"] == 2


@pytest.mark.asyncio
async def test_sorting_by_value(seeded_client: AsyncClient) -> None:
    """Sorting: verify sort by value ascending/descending returns correct order."""
    # Create opportunities with different values
    await seeded_client.post(
        "/opportunities",
        json={"title": "Small Deal", "account_id": 1, "value": 1000},
    )
    await seeded_client.post(
        "/opportunities",
        json={"title": "Medium Deal", "account_id": 1, "value": 5000},
    )
    await seeded_client.post(
        "/opportunities",
        json={"title": "Big Deal", "account_id": 1, "value": 10000},
    )

    # Sort ascending
    response_asc = await seeded_client.get(
        "/opportunities", params={"sort_by": "value", "sort_order": "asc"}
    )
    assert response_asc.status_code == 200
    items_asc = response_asc.json()["data"]
    values_asc = [float(o["value"]) for o in items_asc if o["value"]]
    assert values_asc == sorted(values_asc)

    # Sort descending
    response_desc = await seeded_client.get(
        "/opportunities", params={"sort_by": "value", "sort_order": "desc"}
    )
    assert response_desc.status_code == 200
    items_desc = response_desc.json()["data"]
    values_desc = [float(o["value"]) for o in items_desc if o["value"]]
    assert values_desc == sorted(values_desc, reverse=True)
