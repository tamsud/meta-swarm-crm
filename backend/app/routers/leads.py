"""Leads router — CRUD + conversion endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.lead import LeadStatus
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.schemas.opportunity import OpportunityResponse
from app.services import lead_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("")
async def list_leads(
    status: LeadStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=256),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> dict:
    items, total = await lead_service.list_leads(
        db, current_user, status=status, search=search, offset=offset, limit=limit
    )
    return {
        "items": [LeadResponse.model_validate(l).model_dump() for l in items],
        "meta": {"count": len(items), "total": total, "offset": offset, "limit": limit},
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> LeadResponse:
    lead = await lead_service.get_lead(db, lead_id, current_user)
    return LeadResponse.model_validate(lead)


@router.post("", response_model=LeadResponse, status_code=201)
async def create_lead(
    data: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> LeadResponse:
    lead = await lead_service.create_lead(db, data, current_user)
    return LeadResponse.model_validate(lead)


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> LeadResponse:
    lead = await lead_service.update_lead(db, lead_id, data, current_user)
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> None:
    await lead_service.delete_lead(db, lead_id, current_user)


@router.post("/{lead_id}/convert", response_model=OpportunityResponse, status_code=201)
async def convert_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("leads:manage-own")),
) -> OpportunityResponse:
    opportunity = await lead_service.convert_lead(db, lead_id, current_user)
    return OpportunityResponse.model_validate(opportunity)
