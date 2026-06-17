"""Dashboard router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_summary(
    activity_page: int = Query(default=1, ge=1),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("dashboard:view")),
) -> DashboardSummaryResponse:
    return await dashboard_service.get_summary(db, activity_page=activity_page)
