from datetime import date
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
from app.services.analytics_service import daily_summary, hourly_heatmap, item_velocity, table_turns

router = APIRouter(prefix="/analytics", tags=["analytics"])


class CustomQueryRequest(BaseModel):
    dimension: str
    metric: str
    days: int = 7


@router.get("/summary")
async def get_summary(
    for_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    return DataResponse(data=await daily_summary(db, cu["tenant_id"], for_date))


@router.get("/heatmap")
async def get_heatmap(
    days: int = Query(default=28, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    return DataResponse(data=await hourly_heatmap(db, cu["tenant_id"], days))


@router.get("/velocity")
async def get_velocity(
    days: int = Query(default=14, ge=7, le=30),
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    return DataResponse(data=await item_velocity(db, cu["tenant_id"], days))


@router.get("/table-turns")
async def get_table_turns(
    days: int = Query(default=7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    return DataResponse(data=await table_turns(db, cu["tenant_id"], days))


@router.get("/waiter-performance")
async def get_waiter_performance(
    for_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    from app.services.analytics_service import waiter_performance_today
    return DataResponse(data=await waiter_performance_today(db, cu["tenant_id"], for_date))


@router.post("/custom-query")
async def run_custom(
    body: CustomQueryRequest,
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    from app.services.analytics_query import run_custom_query
    return DataResponse(data=await run_custom_query(db, cu["tenant_id"], body.dimension, body.metric, body.days))
