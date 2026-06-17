"""Mock Email router - API endpoints for mock email inbox.

Permission codes required:
- mock-email:view (grants access to all endpoints)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.mock_email import (
    MockEmailCreate,
    MockEmailDetail,
    MockEmailListItem,
)
from app.services import mock_email_service

router = APIRouter(prefix="/mock-emails", tags=["mock-email"])


@router.get("")
async def list_mock_emails(
    sort: str | None = Query(
        default=None,
        description="Sort field: subject, -subject, date, -date (prefix - for descending). Default: -date",
    ),
    search: str | None = Query(
        default=None,
        max_length=255,
        description="Search by subject (case-insensitive contains)",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("mock-email:view")),
) -> dict:
    """List mock emails with sorting, search, and pagination.

    Sort values:
    - `subject` - alphabetical ascending
    - `-subject` - alphabetical descending
    - `date` - oldest first
    - `-date` - newest first (default)

    Requires mock-email:view permission.
    """
    items, total = await mock_email_service.list_mock_emails(
        db, sort=sort, search=search, offset=offset, limit=limit
    )
    return {
        "items": [item.model_dump() for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.get("/{email_id}", response_model=MockEmailDetail)
async def get_mock_email(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("mock-email:view")),
) -> MockEmailDetail:
    """Get a mock email by ID.

    Side effect: Marks the email as "read" when viewed.

    Requires mock-email:view permission.
    """
    return await mock_email_service.get_mock_email(db, email_id)


@router.post("", response_model=MockEmailDetail, status_code=201)
async def compose_mock_email(
    email_data: MockEmailCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("mock-email:view")),
) -> MockEmailDetail:
    """Compose a new mock email.

    The from_email is automatically set to "crm@demo.local".
    The status is automatically set to "unread".

    Requires mock-email:view permission.
    """
    return await mock_email_service.create_mock_email(db, email_data)


@router.patch("/{email_id}/read", response_model=MockEmailDetail)
async def mark_as_read(
    email_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("mock-email:view")),
) -> MockEmailDetail:
    """Explicitly mark a mock email as read.

    This is useful for batch operations or programmatic use.
    Note: GET /mock-emails/{id} also marks emails as read as a side effect.

    Requires mock-email:view permission.
    """
    return await mock_email_service.mark_as_read(db, email_id)


@router.delete("")
async def clear_mock_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("mock-email:view")),
) -> dict:
    """Delete all mock emails.

    This is a bulk operation that removes all emails from the inbox.
    The operation is idempotent - calling it when there are no emails
    will succeed and return a count of 0.

    Requires mock-email:view permission.
    """
    count = await mock_email_service.clear_mock_emails(db)
    return {"deleted_count": count}
