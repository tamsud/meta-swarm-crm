"""Dashboard schemas for summary response."""

from datetime import datetime

from pydantic import BaseModel

from app.models.activity import ActivityType


class KpiData(BaseModel):
    total_accounts: int
    active_leads: int
    open_pipeline: float
    weighted_value: float
    win_rate: float


class StageBreakdown(BaseModel):
    stage: str
    count: int
    value: float


class ClosedCard(BaseModel):
    count: int
    value: float


class ClosedData(BaseModel):
    won: ClosedCard
    lost: ClosedCard


class ActivitySummary(BaseModel):
    id: int
    type: ActivityType
    subject: str
    contact_name: str | None
    opportunity_title: str | None
    activity_date: datetime


class PaginatedActivities(BaseModel):
    items: list[ActivitySummary]
    total: int
    page: int
    page_size: int
    total_pages: int


class DashboardSummaryResponse(BaseModel):
    kpis: KpiData
    stage_breakdown: list[StageBreakdown]
    closed: ClosedData
    recent_activities: PaginatedActivities
