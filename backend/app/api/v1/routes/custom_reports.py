"""CRUD for tenant custom report cards."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.custom_report import CustomReport
from app.schemas.common import DataResponse

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)

router = APIRouter(prefix="/custom-reports", tags=["custom-reports"])

VALID_CHARTS = {"bar", "line", "pie", "table"}


class ReportBody(BaseModel):
    name: str
    metric: str
    chart_type: str = "bar"
    telegram_schedule: str | None = None
    dimension: str | None = None
    days: int = 7


def _row(r: CustomReport) -> dict:
    return {"id": str(r.id), "name": r.name, "metric": r.metric, "chart_type": r.chart_type,
            "telegram_schedule": r.telegram_schedule, "dimension": r.dimension, "days": r.days}


@router.get("")
async def list_reports(db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    rows = await db.execute(select(CustomReport).where(CustomReport.tenant_id == cu["tenant_id"]))
    return DataResponse(data=[_row(r) for r in rows.scalars()])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_report(body: ReportBody, db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    if body.chart_type not in VALID_CHARTS:
        raise HTTPException(400, f"chart_type must be one of: {', '.join(VALID_CHARTS)}")
    r = CustomReport(tenant_id=cu["tenant_id"], name=body.name, metric=body.metric,
                     chart_type=body.chart_type, telegram_schedule=body.telegram_schedule,
                     dimension=body.dimension, days=body.days)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return DataResponse(data=_row(r))


@router.patch("/{report_id}")
async def update_report(report_id: uuid.UUID, body: ReportBody,
                        db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    r = await db.get(CustomReport, report_id)
    if not r or r.tenant_id != cu["tenant_id"]:
        raise HTTPException(404, "Report not found")
    r.name = body.name
    r.metric = body.metric
    r.chart_type = body.chart_type
    r.telegram_schedule = body.telegram_schedule
    r.dimension = body.dimension
    r.days = body.days
    await db.commit()
    return DataResponse(data=_row(r))


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: uuid.UUID, db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    r = await db.get(CustomReport, report_id)
    if not r or r.tenant_id != cu["tenant_id"]:
        raise HTTPException(404, "Report not found")
    await db.delete(r)
    await db.commit()
