"""Opportunities router - CRUD endpoints for opportunity management.

Permission codes required (from 0003_seed_permissions.py):
- opportunities:create
- opportunities:read
- opportunities:update
- opportunities:delete (Manager/Admin only)
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.opportunity import OpportunityStage
from app.models.user import User
from app.schemas.opportunity import (
    OpportunityCreate,
    OpportunityResponse,
    OpportunityUpdate,
)
from app.services import opportunity_service

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("")
async def list_opportunities(
    stage: OpportunityStage | None = Query(
        default=None,
        description="Filter by pipeline stage",
    ),
    account_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by account ID",
    ),
    contact_id: int | None = Query(
        default=None,
        gt=0,
        description="Filter by contact ID",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max records to return"),
    sort_by: str | None = Query(
        default=None,
        description="Field to sort by (value, expected_close_date, created_at, id)",
    ),
    sort_order: str = Query(
        default="asc",
        regex="^(asc|desc)$",
        description="Sort order (asc or desc)",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("opportunities:read")),
) -> dict:
    """List opportunities with filters, sorting, and pagination.

    Returns opportunities matching the filter criteria with pagination metadata.
    Requires opportunities:read permission.
    """
    opportunities, total = await opportunity_service.list_opportunities(
        db,
        stage=stage,
        account_id=account_id,
        contact_id=contact_id,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    items = [OpportunityResponse.model_validate(o) for o in opportunities]
    return {
        "items": [item.model_dump(mode="json") for item in items],
        "meta": {
            "count": len(items),
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("opportunities:read")),
) -> OpportunityResponse:
    """Get a single opportunity by ID.

    Requires opportunities:read permission.
    """
    opportunity = await opportunity_service.get_opportunity(db, opportunity_id)
    return OpportunityResponse.model_validate(opportunity)


@router.post("", response_model=OpportunityResponse, status_code=201)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("opportunities:create")),
) -> OpportunityResponse:
    """Create a new opportunity.

    If stage is not provided, defaults to 'prospecting'.
    Requires opportunities:create permission.
    """
    opportunity = await opportunity_service.create_opportunity(db, opportunity_data)
    return OpportunityResponse.model_validate(opportunity)


@router.patch("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: int,
    opportunity_data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("opportunities:update")),
) -> OpportunityResponse:
    """Update an existing opportunity.

    Any-to-any stage transitions are allowed.
    Requires opportunities:update permission.
    """
    opportunity = await opportunity_service.update_opportunity(
        db, opportunity_id, opportunity_data
    )
    return OpportunityResponse.model_validate(opportunity)


@router.delete("/{opportunity_id}", status_code=204)
async def delete_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("opportunities:delete")),
) -> None:
    """Delete an opportunity.

    Returns 404 if opportunity not found.
    Requires opportunities:delete permission (Manager/Admin only).
    Sales Rep role does not have this permission - returns 403.
    """
    await opportunity_service.delete_opportunity(db, opportunity_id)
