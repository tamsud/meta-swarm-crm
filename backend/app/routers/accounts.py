"""Accounts router - CRUD endpoints for account management.

Note: This router is initially implemented without permission gating.
Authentication module (WU-AUTH-3) will add require_permission("accounts:{action}")
to all endpoints when it's built.

Permission codes required (from 0003_seed_permissions.py):
- accounts:create
- accounts:read
- accounts:update
- accounts:delete
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("")
async def list_accounts(
    search: str | None = Query(
        default=None,
        max_length=256,
        description="Partial name search (case-insensitive)",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List accounts with search, sorting, and pagination.

    Returns accounts matching the search criteria with pagination metadata.

    TODO: Add require_permission("accounts:read") dependency when Auth module is built.
    """
    accounts, total = await account_service.list_accounts(
        db, search=search, offset=offset, limit=limit
    )
    items = [AccountResponse.model_validate(a) for a in accounts]
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    """Get a single account by ID.

    TODO: Add require_permission("accounts:read") dependency when Auth module is built.
    """
    account = await account_service.get_account(db, account_id)
    return AccountResponse.model_validate(account)


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    """Create a new account.

    TODO: Add require_permission("accounts:create") dependency when Auth module is built.
    """
    account = await account_service.create_account(db, account_data)
    return AccountResponse.model_validate(account)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    """Update an existing account.

    TODO: Add require_permission("accounts:update") dependency when Auth module is built.
    """
    account = await account_service.update_account(db, account_id, account_data)
    return AccountResponse.model_validate(account)


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an account.

    Returns 404 if account not found.
    Returns 409 if account has associated contacts or opportunities.

    TODO: Add require_permission("accounts:delete") dependency when Auth module is built.
    Users without accounts:delete permission will receive 403 once Auth module is implemented.
    """
    await account_service.delete_account(db, account_id)
