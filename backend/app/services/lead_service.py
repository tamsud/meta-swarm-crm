"""Lead service — CRUD, state machine, ownership, atomic conversion."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InvalidLeadTransitionError,
    LeadAlreadyConvertedError,
    LeadNotFoundError,
    LeadOwnershipError,
)
from app.models.account import Account
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.opportunity import Opportunity, OpportunityStage
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate

VALID_TRANSITIONS: dict[LeadStatus, list[LeadStatus]] = {
    LeadStatus.new: [LeadStatus.contacted, LeadStatus.lost],
    LeadStatus.contacted: [LeadStatus.qualified, LeadStatus.lost],
    LeadStatus.qualified: [LeadStatus.lost],
    LeadStatus.lost: [],
}


def _has_manage_all(user: User) -> bool:
    if user.role is None:
        return False
    return any(p.code == "leads:manage-all" for p in user.role.permissions)


def _apply_ownership_filter(stmt: Any, user: User) -> Any:
    if not _has_manage_all(user):
        stmt = stmt.where(Lead.created_by_user_id == user.id)
    return stmt


def _assert_ownership(lead: Lead, user: User) -> None:
    if not _has_manage_all(user) and lead.created_by_user_id != user.id:
        raise LeadOwnershipError()


def validate_status_transition(current: LeadStatus, next_status: LeadStatus) -> None:
    allowed = VALID_TRANSITIONS.get(current, [])
    if next_status not in allowed:
        raise InvalidLeadTransitionError(current.value, next_status.value)


async def create_lead(db: AsyncSession, data: LeadCreate, current_user: User) -> Lead:
    lead = Lead(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        status=data.status,
        source=data.source,
        notes=data.notes,
        created_by_user_id=current_user.id,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def get_lead(db: AsyncSession, lead_id: int, current_user: User) -> Lead:
    stmt = select(Lead).where(Lead.id == lead_id)
    stmt = _apply_ownership_filter(stmt, current_user)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()
    if lead is None:
        raise LeadNotFoundError()
    return lead


async def list_leads(
    db: AsyncSession,
    current_user: User,
    *,
    status: LeadStatus | None = None,
    search: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Lead], int]:
    from sqlalchemy import or_, func as sa_func  # noqa: F401

    base = select(Lead)
    base = _apply_ownership_filter(base, current_user)

    if status is not None:
        base = base.where(Lead.status == status)
    if search:
        pattern = f"%{search}%"
        base = base.where(
            or_(
                Lead.first_name.ilike(pattern),
                Lead.last_name.ilike(pattern),
                Lead.email.ilike(pattern),
                Lead.company.ilike(pattern),
            )
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = base.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
    items = list((await db.execute(stmt)).scalars().all())
    return items, total


async def update_lead(
    db: AsyncSession,
    lead_id: int,
    data: LeadUpdate,
    current_user: User,
) -> Lead:
    lead = await get_lead(db, lead_id, current_user)
    _assert_ownership(lead, current_user)

    if data.status is not None and data.status != lead.status:
        if lead.converted_opportunity_id is not None:
            raise InvalidLeadTransitionError(lead.status.value, data.status.value)
        validate_status_transition(lead.status, data.status)
        lead.status = data.status

    for field in ("first_name", "last_name", "email", "phone", "company", "source", "notes"):
        val = getattr(data, field)
        if val is not None:
            setattr(lead, field, val)

    lead.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(lead)
    return lead


async def delete_lead(db: AsyncSession, lead_id: int, current_user: User) -> None:
    lead = await get_lead(db, lead_id, current_user)
    _assert_ownership(lead, current_user)
    await db.delete(lead)
    await db.commit()


async def convert_lead(db: AsyncSession, lead_id: int, current_user: User) -> Opportunity:
    """Atomically convert a qualified lead to Account + Contact + Opportunity.

    Uses flush-only inline ORM operations within a single transaction.
    Does NOT call external service functions (they commit internally).
    """
    lead = await get_lead(db, lead_id, current_user)

    if lead.converted_opportunity_id is not None:
        raise LeadAlreadyConvertedError(lead.converted_opportunity_id)
    if lead.status != LeadStatus.qualified:
        raise InvalidLeadTransitionError(lead.status.value, "converted")

    now = datetime.now(timezone.utc)

    # All writes happen in the session's implicit transaction (autobegin).
    # Single db.commit() at the end commits atomically.

    # Step 1: find or create Account by company name (case-insensitive)
    company_name = (lead.company or "Unknown Company").strip()
    acct_stmt = select(Account).where(func.lower(Account.name) == company_name.lower())
    acct_result = await db.execute(acct_stmt)
    account = acct_result.scalar_one_or_none()
    if account is None:
        account = Account(name=company_name)
        db.add(account)
        await db.flush()

    # Step 2: find or create Contact by email
    cont_stmt = select(Contact).where(Contact.email == lead.email)
    cont_result = await db.execute(cont_stmt)
    contact = cont_result.scalar_one_or_none()
    if contact is None:
        contact = Contact(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,
            account_id=account.id,
        )
        db.add(contact)
        await db.flush()

    # Step 3: create Opportunity
    opportunity = Opportunity(
        title=f"{company_name} — Converted Lead",
        account_id=account.id,
        contact_id=contact.id,
        stage=OpportunityStage.prospecting,
    )
    db.add(opportunity)
    await db.flush()

    # Step 4: update lead
    lead.converted_opportunity_id = opportunity.id
    lead.converted_at = now
    lead.updated_at = now

    # Single commit — all 4 steps succeed or none do
    await db.commit()
    await db.refresh(opportunity)
    return opportunity
