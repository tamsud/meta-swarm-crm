"""Activities router — CRUD endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.activity import ActivityType
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityUpdate
from app.services import activity_service

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("")
async def list_activities(
    type: ActivityType | None = Query(default=None),
    contact_id: int | None = Query(default=None, gt=0),
    opportunity_id: int | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("activities:manage-own")),
) -> dict:
    items, total = await activity_service.list_activities(
        db,
        current_user,
        type=type,
        contact_id=contact_id,
        opportunity_id=opportunity_id,
        offset=offset,
        limit=limit,
    )
    return {
        "items": [ActivityResponse.model_validate(a).model_dump() for a in items],
        "meta": {"count": len(items), "total": total, "offset": offset, "limit": limit},
    }


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("activities:manage-own")),
) -> ActivityResponse:
    activity = await activity_service.get_activity(db, activity_id, current_user)
    return ActivityResponse.model_validate(activity)


@router.post("", response_model=ActivityResponse, status_code=201)
async def create_activity(
    data: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("activities:manage-own")),
) -> ActivityResponse:
    activity = await activity_service.create_activity(db, data, current_user)
    return ActivityResponse.model_validate(activity)


@router.patch("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("activities:manage-own")),
) -> ActivityResponse:
    activity = await activity_service.update_activity(db, activity_id, data, current_user)
    return ActivityResponse.model_validate(activity)


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("activities:manage-own")),
) -> None:
    await activity_service.delete_activity(db, activity_id, current_user)
