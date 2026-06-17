"""Opportunity service - CRUD operations with business rules."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.exceptions import (
    InvalidAccountIdError,
    InvalidContactIdError,
    OpportunityNotFoundError,
)
from app.models.account import Account
from app.models.contact import Contact
from app.models.opportunity import Opportunity, OpportunityStage
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate

settings = get_settings()


async def create_opportunity(
    db: AsyncSession,
    opportunity_data: OpportunityCreate,
) -> Opportunity:
    """Create a new opportunity.

    Args:
        db: Async database session.
        opportunity_data: Opportunity creation data.

    Returns:
        The created Opportunity.

    Raises:
        InvalidAccountIdError: If account_id does not exist.
        InvalidContactIdError: If contact_id is provided but does not exist.
    """
    # Validate account_id exists
    account_stmt = select(Account).where(Account.id == opportunity_data.account_id)
    result = await db.execute(account_stmt)
    if result.scalar_one_or_none() is None:
        raise InvalidAccountIdError(opportunity_data.account_id)

    # Validate contact_id exists if provided
    if opportunity_data.contact_id is not None:
        contact_stmt = select(Contact).where(Contact.id == opportunity_data.contact_id)
        result = await db.execute(contact_stmt)
        if result.scalar_one_or_none() is None:
            raise InvalidContactIdError(opportunity_data.contact_id)

    # Default stage to prospecting if not provided
    stage = opportunity_data.stage or OpportunityStage.prospecting

    opportunity = Opportunity(
        title=opportunity_data.title,
        account_id=opportunity_data.account_id,
        contact_id=opportunity_data.contact_id,
        stage=stage,
        value=opportunity_data.value,
        probability=opportunity_data.probability,
        expected_close_date=opportunity_data.expected_close_date,
    )
    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)
    return opportunity


async def get_opportunity(
    db: AsyncSession,
    opportunity_id: int,
) -> Opportunity:
    """Get an opportunity by ID.

    Args:
        db: Async database session.
        opportunity_id: The opportunity ID to fetch.

    Returns:
        The Opportunity.

    Raises:
        OpportunityNotFoundError: If opportunity doesn't exist.
    """
    stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
    result = await db.execute(stmt)
    opportunity = result.scalar_one_or_none()

    if opportunity is None:
        raise OpportunityNotFoundError()

    return opportunity


async def list_opportunities(
    db: AsyncSession,
    *,
    stage: OpportunityStage | None = None,
    account_id: int | None = None,
    contact_id: int | None = None,
    offset: int = 0,
    limit: int | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> tuple[list[Opportunity], int]:
    """List opportunities with optional filters, pagination, and sorting.

    Args:
        db: Async database session.
        stage: Optional stage filter.
        account_id: Optional account ID filter.
        contact_id: Optional contact ID filter.
        offset: Number of records to skip (default 0).
        limit: Maximum number of records to return (defaults to Settings.DEFAULT_PAGE_SIZE).
        sort_by: Field to sort by (value, expected_close_date, created_at, id).
        sort_order: Sort order (asc or desc).

    Returns:
        Tuple of (list of Opportunity objects, total count).
    """
    if limit is None:
        limit = settings.DEFAULT_PAGE_SIZE

    # Build base query with optional filters
    base_query = select(Opportunity)

    if stage is not None:
        base_query = base_query.where(Opportunity.stage == stage)

    if account_id is not None:
        base_query = base_query.where(Opportunity.account_id == account_id)

    if contact_id is not None:
        base_query = base_query.where(Opportunity.contact_id == contact_id)

    # Count query
    count_stmt = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Determine sort column
    sort_columns = {
        "value": Opportunity.value,
        "expected_close_date": Opportunity.expected_close_date,
        "created_at": Opportunity.created_at,
        "id": Opportunity.id,
    }
    sort_column = sort_columns.get(sort_by, Opportunity.id)

    # Apply sort order
    if sort_order.lower() == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # Data query with pagination and sorting
    stmt = base_query.order_by(sort_column).offset(offset).limit(limit)
    result = await db.execute(stmt)
    opportunities = list(result.scalars().all())

    return opportunities, total


async def update_opportunity(
    db: AsyncSession,
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
) -> Opportunity:
    """Update an existing opportunity.

    Any-to-any stage transitions are allowed (no sequence restrictions).

    Args:
        db: Async database session.
        opportunity_id: The opportunity ID to update.
        opportunity_data: Updated opportunity data.

    Returns:
        The updated Opportunity.

    Raises:
        OpportunityNotFoundError: If opportunity doesn't exist.
        InvalidAccountIdError: If new account_id doesn't exist.
        InvalidContactIdError: If new contact_id doesn't exist.
    """
    opportunity = await get_opportunity(db, opportunity_id)

    # Validate new account_id if provided
    if opportunity_data.account_id is not None:
        account_stmt = select(Account).where(Account.id == opportunity_data.account_id)
        result = await db.execute(account_stmt)
        if result.scalar_one_or_none() is None:
            raise InvalidAccountIdError(opportunity_data.account_id)
        opportunity.account_id = opportunity_data.account_id

    # Validate new contact_id if provided
    if opportunity_data.contact_id is not None:
        contact_stmt = select(Contact).where(Contact.id == opportunity_data.contact_id)
        result = await db.execute(contact_stmt)
        if result.scalar_one_or_none() is None:
            raise InvalidContactIdError(opportunity_data.contact_id)
        opportunity.contact_id = opportunity_data.contact_id

    # Update other fields
    if opportunity_data.title is not None:
        opportunity.title = opportunity_data.title

    if opportunity_data.stage is not None:
        # Any-to-any stage transition allowed
        opportunity.stage = opportunity_data.stage

    if opportunity_data.value is not None:
        opportunity.value = opportunity_data.value

    if opportunity_data.probability is not None:
        opportunity.probability = opportunity_data.probability

    if opportunity_data.expected_close_date is not None:
        opportunity.expected_close_date = opportunity_data.expected_close_date

    # Update timestamp
    opportunity.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(opportunity)
    return opportunity


async def delete_opportunity(
    db: AsyncSession,
    opportunity_id: int,
) -> None:
    """Delete an opportunity.

    Args:
        db: Async database session.
        opportunity_id: The opportunity ID to delete.

    Raises:
        OpportunityNotFoundError: If opportunity doesn't exist.
    """
    opportunity = await get_opportunity(db, opportunity_id)
    await db.delete(opportunity)
    await db.commit()
