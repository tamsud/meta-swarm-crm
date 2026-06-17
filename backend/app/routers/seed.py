"""Seed router — POST /seed and DELETE /seed for admin data management."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.dependencies import require_permission
from app.database import get_db
from app.models.user import User
from app.seed import clear_all, seed_all

router = APIRouter(prefix="/seed", tags=["seed"])


@router.post("")
async def run_seed(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("seed:manage")),
) -> dict:
    summary = await seed_all(db)
    return {"summary": summary}


@router.delete("")
async def run_clear(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission("seed:manage")),
) -> dict:
    counts = await clear_all(db)
    return {"deleted": counts}
