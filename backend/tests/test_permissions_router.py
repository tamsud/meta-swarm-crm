"""Tests for the permissions router."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models.permission import Permission


@pytest_asyncio.fixture
async def seeded_client() -> AsyncClient:
    """Create a test client with seeded permissions."""
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

    # Seed permissions
    async with TestSessionLocal() as session:
        permissions_data = [
            ("accounts:create", "accounts", "create", "Create accounts"),
            ("accounts:read", "accounts", "read", "Read accounts"),
            ("leads:manage-own", "leads", "manage-own", "Manage own leads"),
            ("leads:manage-all", "leads", "manage-all", "Manage all leads"),
        ]
        for code, module, action, desc in permissions_data:
            session.add(
                Permission(code=code, module=module, action=action, description=desc)
            )
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
async def test_get_permissions_returns_catalogue(seeded_client: AsyncClient) -> None:
    """GET /permissions returns the full catalogue."""
    response = await seeded_client.get("/permissions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    codes = {p["code"] for p in data}
    assert codes == {
        "accounts:create",
        "accounts:read",
        "leads:manage-own",
        "leads:manage-all",
    }


@pytest.mark.asyncio
async def test_get_permissions_with_module_filter(seeded_client: AsyncClient) -> None:
    """GET /permissions?module=leads returns only leads permissions."""
    response = await seeded_client.get("/permissions", params={"module": "leads"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    codes = {p["code"] for p in data}
    assert codes == {"leads:manage-own", "leads:manage-all"}


@pytest.mark.asyncio
async def test_get_permissions_with_unknown_module_returns_empty(
    seeded_client: AsyncClient,
) -> None:
    """GET /permissions?module=nonexistent returns empty list."""
    response = await seeded_client.get("/permissions", params={"module": "nonexistent"})

    assert response.status_code == 200
    assert response.json() == []


def test_no_post_patch_delete_endpoints_for_permissions() -> None:
    """Route-table inspection: no POST/PATCH/DELETE handlers for /permissions.

    This test asserts the read-only contract programmatically via route inspection,
    not by sending requests and checking for 404/405.
    """
    forbidden_methods = {"POST", "PATCH", "DELETE", "PUT"}

    for route in app.routes:
        if hasattr(route, "path") and route.path == "/permissions":
            if hasattr(route, "methods"):
                route_methods = set(route.methods)
                overlap = route_methods & forbidden_methods
                assert not overlap, (
                    f"/permissions route has forbidden methods: {overlap}"
                )
