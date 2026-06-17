"""Contact service - CRUD operations with business rules."""

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    ContactEmailConflictError,
    ContactNotFoundError,
    InvalidAccountIdError,
)
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from app.services import account_service

settings = get_settings()


async def create_contact(
    db: AsyncSession,
    contact_data: ContactCreate,
) -> Contact:
    """Create a new contact.

    Args:
        db: Async database session.
        contact_data: Contact creation data.

    Returns:
        The created Contact.

    Raises:
        ContactEmailConflictError: If a contact with the same email exists (case-insensitive).
        InvalidAccountIdError: If the specified account_id does not exist.
    """
    # Validate account_id if provided
    if contact_data.account_id is not None:
        try:
            await account_service.get_account(db, contact_data.account_id)
        except Exception:
            raise InvalidAccountIdError(contact_data.account_id)

    # Check for email uniqueness (case-insensitive)
    existing = await find_by_email(db, contact_data.email)
    if existing is not None:
        raise ContactEmailConflictError()

    contact = Contact(
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        email=contact_data.email.strip(),
        phone=contact_data.phone,
        job_title=contact_data.job_title,
        account_id=contact_data.account_id,
    )
    db.add(contact)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ContactEmailConflictError()

    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contact(
    db: AsyncSession,
    contact_id: int,
) -> Contact:
    """Get a contact by ID.

    Args:
        db: Async database session.
        contact_id: The contact ID to fetch.

    Returns:
        The Contact.

    Raises:
        ContactNotFoundError: If contact doesn't exist.
    """
    stmt = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact is None:
        raise ContactNotFoundError()

    return contact


async def list_contacts(
    db: AsyncSession,
    *,
    search: str | None = None,
    account_id: int | None = None,
    sort: str | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[Contact], int]:
    """List contacts with optional filtering, sorting, and pagination.

    Args:
        db: Async database session.
        search: Optional partial search on first_name, last_name, email (case-insensitive).
        account_id: Optional filter by account_id.
        sort: Optional sort field with optional '-' prefix for descending.
              Supported fields: first_name, last_name, email, created_at, updated_at.
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (defaults to Settings.DEFAULT_PAGE_SIZE).

    Returns:
        Tuple of (list of Contact objects, total count).
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    # Build base query with optional filters
    base_query = select(Contact)

    if search:
        search_pattern = f"%{search}%"
        base_query = base_query.where(
            or_(
                func.lower(Contact.first_name).like(func.lower(search_pattern)),
                func.lower(Contact.last_name).like(func.lower(search_pattern)),
                func.lower(Contact.email).like(func.lower(search_pattern)),
            )
        )

    if account_id is not None:
        base_query = base_query.where(Contact.account_id == account_id)

    # Count query
    count_stmt = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Determine sort order
    order_column = Contact.id  # Default sort
    descending = False

    if sort:
        if sort.startswith("-"):
            descending = True
            sort_field = sort[1:]
        else:
            sort_field = sort

        # Map sort field to column
        sort_mapping = {
            "first_name": Contact.first_name,
            "last_name": Contact.last_name,
            "email": Contact.email,
            "created_at": Contact.created_at,
            "updated_at": Contact.updated_at,
            "id": Contact.id,
        }
        order_column = sort_mapping.get(sort_field, Contact.id)

    if descending:
        order_clause = order_column.desc()
    else:
        order_clause = order_column.asc()

    # Data query with sorting and pagination
    stmt = base_query.order_by(order_clause).offset(offset).limit(limit)
    result = await db.execute(stmt)
    contacts = list(result.scalars().all())

    return contacts, total


async def update_contact(
    db: AsyncSession,
    contact_id: int,
    contact_data: ContactUpdate,
) -> Contact:
    """Update an existing contact.

    Args:
        db: Async database session.
        contact_id: The contact ID to update.
        contact_data: Updated contact data.

    Returns:
        The updated Contact.

    Raises:
        ContactNotFoundError: If contact doesn't exist.
        ContactEmailConflictError: If new email conflicts with existing contact.
        InvalidAccountIdError: If new account_id doesn't exist.
    """
    contact = await get_contact(db, contact_id)

    # Validate email uniqueness if email is being changed
    if contact_data.email is not None and contact_data.email.lower() != contact.email.lower():
        existing = await find_by_email(db, contact_data.email)
        if existing is not None:
            raise ContactEmailConflictError()

    # Validate account_id if being changed
    if contact_data.account_id is not None and contact_data.account_id != contact.account_id:
        try:
            await account_service.get_account(db, contact_data.account_id)
        except Exception:
            raise InvalidAccountIdError(contact_data.account_id)

    # Update fields
    if contact_data.first_name is not None:
        contact.first_name = contact_data.first_name

    if contact_data.last_name is not None:
        contact.last_name = contact_data.last_name

    if contact_data.email is not None:
        contact.email = contact_data.email.strip()

    if contact_data.phone is not None:
        contact.phone = contact_data.phone

    if contact_data.job_title is not None:
        contact.job_title = contact_data.job_title

    # Handle account_id - can be set to None or a new value
    if "account_id" in contact_data.model_fields_set:
        contact.account_id = contact_data.account_id

    # Update timestamp
    contact.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ContactEmailConflictError()

    await db.refresh(contact)
    return contact


async def delete_contact(
    db: AsyncSession,
    contact_id: int,
) -> None:
    """Delete a contact.

    Args:
        db: Async database session.
        contact_id: The contact ID to delete.

    Raises:
        ContactNotFoundError: If contact doesn't exist.
    """
    contact = await get_contact(db, contact_id)

    await db.delete(contact)
    await db.commit()


async def find_by_email(
    db: AsyncSession,
    email: str,
) -> Contact | None:
    """Find a contact by email (case-insensitive).

    This function is used by Leads module for conversion.

    Args:
        db: Async database session.
        email: The email to search for.

    Returns:
        The Contact if found, None otherwise.
    """
    stmt = select(Contact).where(func.lower(Contact.email) == func.lower(email.strip()))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
