"""Accounts router - CRUD endpoints for account management.

Permission codes required (from 0003_seed_permissions.py):
- accounts:create
- accounts:read
- accounts:update
- accounts:delete
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import get_current_user, require_permission
from app.database import get_db
from app.models.user import User
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
    current_user: User = Depends(require_permission("accounts:read")),
) -> dict:
    """List accounts with search, sorting, and pagination.

    Returns accounts matching the search criteria with pagination metadata.
    Requires accounts:read permission.
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
    current_user: User = Depends(require_permission("accounts:read")),
) -> AccountResponse:
    """Get a single account by ID.

    Requires accounts:read permission.
    """
    account = await account_service.get_account(db, account_id)
    return AccountResponse.model_validate(account)


@router.post("", response_model=AccountResponse, status_code=201)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("accounts:create")),
) -> AccountResponse:
    """Create a new account.

    Requires accounts:create permission.
    """
    account = await account_service.create_account(db, account_data)
    return AccountResponse.model_validate(account)


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("accounts:update")),
) -> AccountResponse:
    """Update an existing account.

    Requires accounts:update permission.
    """
    account = await account_service.update_account(db, account_id, account_data)
    return AccountResponse.model_validate(account)


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("accounts:delete")),
) -> None:
    """Delete an account.

    Returns 404 if account not found.
    Returns 409 if account has associated contacts or opportunities.
    Requires accounts:delete permission.
    """
    await account_service.delete_account(db, account_id)
