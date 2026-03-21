"""Report endpoints including EOD triggers."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.common import DataResponse
from app.schemas.print_template import PrintTemplateConfig

from app.services.analytics_service import daily_summary, waiter_performance_today
from app.services.print_payload import build_eod_payload
from app.services.print_service import create_eod_print_job
from app.services.telegram_service import send_eod_report

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)

router = APIRouter(prefix="/reports", tags=["reports"])


from datetime import date, datetime

class EodTriggerRequest(BaseModel):
    date: str | None = None


@router.post("/eod")
async def trigger_eod(
    body: EodTriggerRequest,
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    """Trigger EOD: Generate summary, send Telegram report, and queue print job."""
    for_date = date.today()
    if body.date:
        try:
            for_date = datetime.strptime(body.date, "%Y-%m-%d").date()
        except ValueError:
            pass
    tenant_id = cu["tenant_id"]

    # 1. Trigger the consolidated EOD flow
    from app.services.eod_service import trigger_eod_flow
    result = await trigger_eod_flow(db, tenant_id, for_date)

    return DataResponse(data=result)
