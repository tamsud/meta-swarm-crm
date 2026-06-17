"""Contacts router - CRUD endpoints for contact management.

Permission codes required (from 0003_seed_permissions.py):
- contacts:create
- contacts:read
- contacts:update
- contacts:delete
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services import contact_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("")
async def list_contacts(
    search: str | None = Query(
        default=None,
        max_length=256,
        description="Partial search on first name, last name, or email (case-insensitive)",
    ),
    account_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by account ID",
    ),
    sort: str | None = Query(
        default=None,
        max_length=64,
        description="Sort field with optional '-' prefix for descending (e.g., '-created_at')",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("contacts:read")),
) -> dict:
    """List contacts with search, filtering, sorting, and pagination.

    Returns contacts matching the criteria with pagination metadata.
    Requires contacts:read permission.
    """
    contacts, total = await contact_service.list_contacts(
        db, search=search, account_id=account_id, sort=sort, offset=offset, limit=limit
    )
    items = [ContactResponse.model_validate(c) for c in contacts]
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("contacts:read")),
) -> ContactResponse:
    """Get a single contact by ID.

    Requires contacts:read permission.
    """
    contact = await contact_service.get_contact(db, contact_id)
    return ContactResponse.model_validate(contact)


@router.post("", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("contacts:create")),
) -> ContactResponse:
    """Create a new contact.

    Requires contacts:create permission.
    """
    contact = await contact_service.create_contact(db, contact_data)
    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("contacts:update")),
) -> ContactResponse:
    """Update an existing contact.

    Requires contacts:update permission.
    """
    contact = await contact_service.update_contact(db, contact_id, contact_data)
    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("contacts:delete")),
) -> None:
    """Delete a contact.

    Returns 404 if contact not found.
    Requires contacts:delete permission.
    """
    await contact_service.delete_contact(db, contact_id)
