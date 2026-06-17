"""Dashboard service — KPI aggregations and activity feed."""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.activity import Activity
from app.models.contact import Contact
from app.models.lead import Lead, LeadStatus
from app.models.opportunity import Opportunity, OpportunityStage
from app.schemas.dashboard import (
    ActivitySummary,
    ClosedCard,
    ClosedData,
    DashboardSummaryResponse,
    KpiData,
    PaginatedActivities,
    StageBreakdown,
)

OPEN_STAGES = (
    OpportunityStage.prospecting,
    OpportunityStage.proposal,
    OpportunityStage.negotiation,
)
CLOSED_WON = OpportunityStage.closed_won
CLOSED_LOST = OpportunityStage.closed_lost
ACTIVITY_PAGE_SIZE = 5


async def get_summary(db: AsyncSession, activity_page: int = 1) -> DashboardSummaryResponse:
    # --- KPIs ---
    total_accounts = (await db.execute(select(func.count(Account.id)))).scalar_one()

    active_statuses = (LeadStatus.new, LeadStatus.contacted, LeadStatus.qualified)
    active_leads = (
        await db.execute(select(func.count(Lead.id)).where(Lead.status.in_(active_statuses)))
    ).scalar_one()

    open_pipeline_result = (
        await db.execute(
            select(func.coalesce(func.sum(Opportunity.value), 0)).where(
                Opportunity.stage.in_(OPEN_STAGES)
            )
        )
    ).scalar_one()
    open_pipeline = float(open_pipeline_result)

    weighted_result = (
        await db.execute(
            select(
                func.coalesce(
                    func.sum(Opportunity.value * Opportunity.probability / 100.0), 0
                )
            ).where(Opportunity.stage.in_(OPEN_STAGES))
        )
    ).scalar_one()
    weighted_value = float(weighted_result)

    won_count = (
        await db.execute(select(func.count(Opportunity.id)).where(Opportunity.stage == CLOSED_WON))
    ).scalar_one()
    lost_count = (
        await db.execute(select(func.count(Opportunity.id)).where(Opportunity.stage == CLOSED_LOST))
    ).scalar_one()
    win_rate = won_count / (won_count + lost_count) if (won_count + lost_count) > 0 else 0.0

    # --- Stage breakdown ---
    stage_breakdown = []
    for stage in OpportunityStage:
        count = (
            await db.execute(select(func.count(Opportunity.id)).where(Opportunity.stage == stage))
        ).scalar_one()
        value = float(
            (
                await db.execute(
                    select(func.coalesce(func.sum(Opportunity.value), 0)).where(
                        Opportunity.stage == stage
                    )
                )
            ).scalar_one()
        )
        stage_breakdown.append(StageBreakdown(stage=stage.value, count=count, value=value))

    # --- Closed deals ---
    won_value = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Opportunity.value), 0)).where(
                    Opportunity.stage == CLOSED_WON
                )
            )
        ).scalar_one()
    )
    lost_value = float(
        (
            await db.execute(
                select(func.coalesce(func.sum(Opportunity.value), 0)).where(
                    Opportunity.stage == CLOSED_LOST
                )
            )
        ).scalar_one()
    )
    closed = ClosedData(
        won=ClosedCard(count=won_count, value=won_value),
        lost=ClosedCard(count=lost_count, value=lost_value),
    )

    # --- Recent activities paginated ---
    activity_total = (await db.execute(select(func.count(Activity.id)))).scalar_one()
    total_pages = max(1, math.ceil(activity_total / ACTIVITY_PAGE_SIZE))
    page = max(1, min(activity_page, total_pages))
    act_offset = (page - 1) * ACTIVITY_PAGE_SIZE

    recent_stmt = (
        select(Activity)
        .order_by(Activity.activity_date.desc())
        .offset(act_offset)
        .limit(ACTIVITY_PAGE_SIZE)
    )
    recent_rows = list((await db.execute(recent_stmt)).scalars().all())

    activity_items = []
    for a in recent_rows:
        contact_name = None
        if a.contact_id and a.contact:
            contact_name = f"{a.contact.first_name} {a.contact.last_name}"
        opp_title = a.opportunity.title if (a.opportunity_id and a.opportunity) else None
        activity_items.append(
            ActivitySummary(
                id=a.id,
                type=a.type,
                subject=a.subject,
                contact_name=contact_name,
                opportunity_title=opp_title,
                activity_date=a.activity_date,
            )
        )

    return DashboardSummaryResponse(
        kpis=KpiData(
            total_accounts=total_accounts,
            active_leads=active_leads,
            open_pipeline=open_pipeline,
            weighted_value=weighted_value,
            win_rate=win_rate,
        ),
        stage_breakdown=stage_breakdown,
        closed=closed,
        recent_activities=PaginatedActivities(
            items=activity_items,
            total=activity_total,
            page=page,
            page_size=ACTIVITY_PAGE_SIZE,
            total_pages=total_pages,
        ),
    )
