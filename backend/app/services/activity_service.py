"""Activity service — CRUD with ownership scoping."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    ActivityNotFoundError,
    ActivityOwnershipError,
    InvalidContactIdError,
    InvalidOpportunityIdError,
)
from app.models.activity import Activity, ActivityType
from app.models.contact import Contact
from app.models.opportunity import Opportunity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate


def _has_manage_all(user: User) -> bool:
    if user.role is None:
        return False
    return any(p.code == "activities:manage-all" for p in user.role.permissions)


def _apply_ownership_filter(stmt: object, user: User) -> object:
    if not _has_manage_all(user):
        stmt = stmt.where(Activity.created_by_user_id == user.id)  # type: ignore[union-attr]
    return stmt


def _assert_ownership(activity: Activity, user: User) -> None:
    if not _has_manage_all(user) and activity.created_by_user_id != user.id:
        raise ActivityOwnershipError()


async def create_activity(
    db: AsyncSession,
    data: ActivityCreate,
    current_user: User,
) -> Activity:
    if data.contact_id is not None:
        result = await db.execute(select(Contact).where(Contact.id == data.contact_id))
        if result.scalar_one_or_none() is None:
            raise InvalidContactIdError(data.contact_id)

    if data.opportunity_id is not None:
        result = await db.execute(select(Opportunity).where(Opportunity.id == data.opportunity_id))
        if result.scalar_one_or_none() is None:
            raise InvalidOpportunityIdError(data.opportunity_id)

    activity = Activity(
        type=data.type,
        subject=data.subject,
        notes=data.notes,
        activity_date=data.activity_date or datetime.now(timezone.utc),
        contact_id=data.contact_id,
        opportunity_id=data.opportunity_id,
        created_by_user_id=current_user.id,
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def get_activity(db: AsyncSession, activity_id: int, current_user: User) -> Activity:
    stmt = select(Activity).where(Activity.id == activity_id)
    stmt = _apply_ownership_filter(stmt, current_user)
    result = await db.execute(stmt)
    activity = result.scalar_one_or_none()
    if activity is None:
        raise ActivityNotFoundError()
    return activity


async def list_activities(
    db: AsyncSession,
    current_user: User,
    *,
    type: ActivityType | None = None,
    contact_id: int | None = None,
    opportunity_id: int | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Activity], int]:
    base = select(Activity)
    base = _apply_ownership_filter(base, current_user)

    if type is not None:
        base = base.where(Activity.type == type)
    if contact_id is not None:
        base = base.where(Activity.contact_id == contact_id)
    if opportunity_id is not None:
        base = base.where(Activity.opportunity_id == opportunity_id)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = base.order_by(Activity.activity_date.desc()).offset(offset).limit(limit)
    items = list((await db.execute(stmt)).scalars().all())
    return items, total


async def update_activity(
    db: AsyncSession,
    activity_id: int,
    data: ActivityUpdate,
    current_user: User,
) -> Activity:
    activity = await get_activity(db, activity_id, current_user)
    _assert_ownership(activity, current_user)

    if data.type is not None:
        activity.type = data.type
    if data.subject is not None:
        activity.subject = data.subject
    if data.notes is not None:
        activity.notes = data.notes
    if data.activity_date is not None:
        activity.activity_date = data.activity_date
    if data.contact_id is not None:
        result = await db.execute(select(Contact).where(Contact.id == data.contact_id))
        if result.scalar_one_or_none() is None:
            raise InvalidContactIdError(data.contact_id)
        activity.contact_id = data.contact_id
    if data.opportunity_id is not None:
        result = await db.execute(select(Opportunity).where(Opportunity.id == data.opportunity_id))
        if result.scalar_one_or_none() is None:
            raise InvalidOpportunityIdError(data.opportunity_id)
        activity.opportunity_id = data.opportunity_id

    activity.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(activity)
    return activity


async def delete_activity(
    db: AsyncSession,
    activity_id: int,
    current_user: User,
) -> None:
    activity = await get_activity(db, activity_id, current_user)
    _assert_ownership(activity, current_user)
    await db.delete(activity)
    await db.commit()
