"""Account service - CRUD operations with business rules."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    AccountHasDependentsError,
    AccountNotFoundError,
    DuplicateAccountNameError,
)
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate

settings = get_settings()


async def create_account(
    db: AsyncSession,
    account_data: AccountCreate,
) -> Account:
    """Create a new account.

    Args:
        db: Async database session.
        account_data: Account creation data.

    Returns:
        The created Account.

    Raises:
        DuplicateAccountNameError: If an account with the same name exists (case-insensitive).
    """
    account = Account(
        name=account_data.name,
        industry=account_data.industry,
        website=account_data.website,
        phone=account_data.phone,
        address=account_data.address,
    )
    db.add(account)

    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise DuplicateAccountNameError()

    await db.commit()
    await db.refresh(account)
    return account


async def get_account(
    db: AsyncSession,
    account_id: int,
) -> Account:
    """Get an account by ID.

    Args:
        db: Async database session.
        account_id: The account ID to fetch.

    Returns:
        The Account.

    Raises:
        AccountNotFoundError: If account doesn't exist.
    """
    stmt = select(Account).where(Account.id == account_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if account is None:
        raise AccountNotFoundError()

    return account


async def list_accounts(
    db: AsyncSession,
    *,
    search: str | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[list[Account], int]:
    """List accounts with optional search and pagination.

    Uses the lower(name) index for case-insensitive search.

    Args:
        db: Async database session.
        search: Optional partial name search (case-insensitive).
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (defaults to Settings.DEFAULT_PAGE_SIZE).

    Returns:
        Tuple of (list of Account objects, total count).
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    # Build base query with optional search filter
    base_query = select(Account)
    if search:
        # Use lower() for case-insensitive search to leverage the functional index
        search_pattern = f"%{search}%"
        base_query = base_query.where(func.lower(Account.name).like(func.lower(search_pattern)))

    # Count query
    count_stmt = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Data query with pagination
    stmt = base_query.order_by(Account.id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    accounts = list(result.scalars().all())

    return accounts, total


async def update_account(
    db: AsyncSession,
    account_id: int,
    account_data: AccountUpdate,
) -> Account:
    """Update an existing account.

    Args:
        db: Async database session.
        account_id: The account ID to update.
        account_data: Updated account data.

    Returns:
        The updated Account.

    Raises:
        AccountNotFoundError: If account doesn't exist.
        DuplicateAccountNameError: If new name conflicts with existing account.
    """
    account = await get_account(db, account_id)

    if account_data.name is not None:
        account.name = account_data.name

    if account_data.industry is not None:
        account.industry = account_data.industry

    if account_data.website is not None:
        account.website = account_data.website

    if account_data.phone is not None:
        account.phone = account_data.phone

    if account_data.address is not None:
        account.address = account_data.address

    # Update timestamp
    account.updated_at = datetime.now(timezone.utc)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise DuplicateAccountNameError()

    await db.refresh(account)
    return account


async def delete_account(
    db: AsyncSession,
    account_id: int,
) -> None:
    """Delete an account.

    Checks for dependent contacts and opportunities before deletion.

    Args:
        db: Async database session.
        account_id: The account ID to delete.

    Raises:
        AccountNotFoundError: If account doesn't exist.
        AccountHasDependentsError: If account has associated contacts or opportunities.
    """
    account = await get_account(db, account_id)

    # TODO: Replace with actual counts once Contacts and Opportunities modules exist
    # contact_count = await db.scalar(
    #     select(func.count()).select_from(Contact).where(Contact.account_id == account_id)
    # )
    # opportunity_count = await db.scalar(
    #     select(func.count()).select_from(Opportunity).where(Opportunity.account_id == account_id)
    # )
    contact_count = 0
    opportunity_count = 0

    if contact_count > 0 or opportunity_count > 0:
        raise AccountHasDependentsError(
            contact_count=contact_count,
            opportunity_count=opportunity_count,
        )

    await db.delete(account)
    await db.commit()


async def find_or_create_by_name(
    db: AsyncSession,
    name: str,
) -> Account:
    """Find an account by name (case-insensitive) or create it if not found.

    This function is atomic and designed for Leads conversion.

    Args:
        db: Async database session.
        name: The account name to find or create.

    Returns:
        The existing or newly created Account.
    """
    # Case-insensitive lookup using the functional index
    stmt = select(Account).where(func.lower(Account.name) == func.lower(name))
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if account is not None:
        return account

    # Account doesn't exist, create it
    account = Account(name=name)
    db.add(account)

    try:
        await db.flush()
        await db.commit()
        await db.refresh(account)
    except IntegrityError:
        # Race condition: another transaction created the account
        await db.rollback()
        # Retry the lookup
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        if account is None:
            # This shouldn't happen, but raise if it does
            raise DuplicateAccountNameError()

    return account
