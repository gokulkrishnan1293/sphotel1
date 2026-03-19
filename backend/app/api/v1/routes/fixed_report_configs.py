"""CRUD for fixed dashboard report card configs (top_items, waiter_performance, payment_breakdown)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.fixed_report_config import FixedReportConfig, FIXED_REPORT_TYPES
from app.schemas.common import DataResponse

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
router = APIRouter(prefix="/fixed-report-configs", tags=["fixed-report-configs"])


class PatchBody(BaseModel):
    telegram_schedule: str | None = None
    is_visible: bool = True


def _row(c: FixedReportConfig) -> dict:
    return {"id": str(c.id), "report_type": c.report_type,
            "telegram_schedule": c.telegram_schedule, "is_visible": c.is_visible}


async def _ensure_seeded(tenant_id, db: AsyncSession) -> list[FixedReportConfig]:
    existing = (await db.execute(
        select(FixedReportConfig).where(FixedReportConfig.tenant_id == tenant_id)
    )).scalars().all()
    missing = set(FIXED_REPORT_TYPES) - {c.report_type for c in existing}
    for rt in missing:
        db.add(FixedReportConfig(tenant_id=tenant_id, report_type=rt))
    if missing:
        await db.commit()
    result = (await db.execute(
        select(FixedReportConfig).where(FixedReportConfig.tenant_id == tenant_id)
    )).scalars().all()
    return list(result)


@router.get("")
async def list_configs(db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    configs = await _ensure_seeded(cu["tenant_id"], db)
    return DataResponse(data=[_row(c) for c in configs])


@router.patch("/{report_type}")
async def update_config(report_type: str, body: PatchBody,
                        db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    await _ensure_seeded(cu["tenant_id"], db)
    result = await db.execute(select(FixedReportConfig).where(
        FixedReportConfig.tenant_id == cu["tenant_id"],
        FixedReportConfig.report_type == report_type,
    ))
    c = result.scalar_one_or_none()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(404, "Report type not found")
    c.telegram_schedule = body.telegram_schedule
    c.is_visible = body.is_visible
    await db.commit()
    return DataResponse(data=_row(c))
