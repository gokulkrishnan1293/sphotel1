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

    # 1. Fetch tenant & template settings
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_id))
    tenant = result.scalar_one()

    template_dict = (
        PrintTemplateConfig(**tenant.print_template).model_dump()
        if tenant.print_template else PrintTemplateConfig().model_dump()
    )

    # 2. Fetch data
    summary = await daily_summary(db, tenant_id, for_date)
    waiter_rows = await waiter_performance_today(db, tenant_id, for_date)

    # 3. Fire to Telegram (runs sync-like here, but it's fine for this trigger)
    telegram_sent = await send_eod_report(db, tenant_id, tenant.name, for_date,
                                          template=template_dict, waiter_rows=waiter_rows)

    # 4. Create print job
    payload = build_eod_payload(summary, waiter_rows, template_dict)
    job = await create_eod_print_job(db, tenant_id, payload)

    return DataResponse(data={
        "telegram_sent": telegram_sent,
        "print_job_id": str(job.id)
    })
