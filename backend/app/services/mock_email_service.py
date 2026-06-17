"""Mock Email service - CRUD operations with business rules."""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import MockEmailNotFoundError
from app.models.mock_email import MockEmail
from app.schemas.mock_email import MockEmailCreate, MockEmailDetail, MockEmailListItem

settings = get_settings()

# Fixed from_email for all mock emails (ADR-EMAIL-3)
MOCK_EMAIL_FROM = "crm@demo.local"

# Preview length for list items (FR-EMAIL-007)
PREVIEW_LENGTH = 80


def _truncate_body(body: str | None) -> str:
    """Truncate body to preview length."""
    if body is None:
        return ""
    if len(body) <= PREVIEW_LENGTH:
        return body
    return body[:PREVIEW_LENGTH] + "..."


async def list_mock_emails(
    db: AsyncSession,
    *,
    sort: str | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[MockEmailListItem], int]:
    """List mock emails with sorting, search, and pagination.

    Args:
        db: Async database session.
        sort: Sort field with optional - prefix for descending.
              Valid values: subject, -subject, date, -date.
              Default: -date (newest first).
        search: Optional subject search (case-insensitive contains).
        offset: Number of records to skip (default 0).
        limit: Maximum records to return (defaults to Settings.DEFAULT_PAGE_SIZE).

    Returns:
        Tuple of (list of MockEmailListItem, total count).
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    # Build base query
    base_query = select(MockEmail)

    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        base_query = base_query.where(
            func.lower(MockEmail.subject).like(func.lower(search_pattern))
        )

    # Count query
    count_stmt = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply sorting
    sort = sort or "-date"  # Default: newest first
    if sort == "subject":
        order_clause = MockEmail.subject.asc()
    elif sort == "-subject":
        order_clause = MockEmail.subject.desc()
    elif sort == "date":
        order_clause = MockEmail.created_at.asc()
    elif sort == "-date":
        order_clause = MockEmail.created_at.desc()
    else:
        # Invalid sort, default to -date
        order_clause = MockEmail.created_at.desc()

    # Data query with pagination
    stmt = base_query.order_by(order_clause).offset(offset).limit(limit)
    result = await db.execute(stmt)
    emails = list(result.scalars().all())

    # Convert to list items with preview
    items = [
        MockEmailListItem(
            id=email.id,
            subject=email.subject,
            from_email=email.from_email,
            to_email=email.to_email,
            preview=_truncate_body(email.body),
            status=email.status,
            created_at=email.created_at,
        )
        for email in emails
    ]

    return items, total


async def get_mock_email(
    db: AsyncSession,
    email_id: str,
) -> MockEmailDetail:
    """Get a mock email by ID and mark it as read.

    This implements ADR-EMAIL-2: viewing an email marks it as read automatically.

    Args:
        db: Async database session.
        email_id: The mock email ID (UUID string).

    Returns:
        The MockEmailDetail.

    Raises:
        MockEmailNotFoundError: If email doesn't exist.
    """
    stmt = select(MockEmail).where(MockEmail.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()

    if email is None:
        raise MockEmailNotFoundError()

    # Mark as read (side effect per ADR-EMAIL-2)
    if email.status == "unread":
        email.status = "read"
        await db.commit()
        await db.refresh(email)

    return MockEmailDetail.model_validate(email)


async def create_mock_email(
    db: AsyncSession,
    email_data: MockEmailCreate,
) -> MockEmailDetail:
    """Create a new mock email.

    Sets from_email to "crm@demo.local" per ADR-EMAIL-3.

    Args:
        db: Async database session.
        email_data: Email creation data (to_email, subject, body).

    Returns:
        The created MockEmailDetail.
    """
    email = MockEmail(
        to_email=email_data.to_email,
        subject=email_data.subject,
        body=email_data.body,
        from_email=MOCK_EMAIL_FROM,
        status="unread",
    )
    db.add(email)
    await db.commit()
    await db.refresh(email)

    return MockEmailDetail.model_validate(email)


async def mark_as_read(
    db: AsyncSession,
    email_id: str,
) -> MockEmailDetail:
    """Explicitly mark a mock email as read.

    Args:
        db: Async database session.
        email_id: The mock email ID (UUID string).

    Returns:
        The updated MockEmailDetail.

    Raises:
        MockEmailNotFoundError: If email doesn't exist.
    """
    stmt = select(MockEmail).where(MockEmail.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()

    if email is None:
        raise MockEmailNotFoundError()

    email.status = "read"
    await db.commit()
    await db.refresh(email)

    return MockEmailDetail.model_validate(email)


async def clear_mock_emails(
    db: AsyncSession,
) -> int:
    """Delete all mock emails.

    Args:
        db: Async database session.

    Returns:
        The number of emails deleted.
    """
    # Count before delete
    count_stmt = select(func.count()).select_from(MockEmail)
    count_result = await db.execute(count_stmt)
    count = count_result.scalar_one()

    # Delete all
    delete_stmt = delete(MockEmail)
    await db.execute(delete_stmt)
    await db.commit()

    return count
