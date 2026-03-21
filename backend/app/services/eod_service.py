from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.schemas.print_template import PrintTemplateConfig
from app.services.analytics_service import daily_summary, waiter_performance_today
from app.services.print_payload import build_eod_payload
from app.services.print_service import create_eod_print_job
from app.services.telegram_service import send_eod_report

async def trigger_eod_flow(db: AsyncSession, tenant_id: str, for_date: date, auto_print: bool = True) -> dict:
    '''Orchestrates EOD summary generation, Telegram reporting, and optionally queueing print jobs.'''
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

    # 3. Fire to Telegram
    telegram_sent = await send_eod_report(db, tenant_id, tenant.name, for_date,
                                          template=template_dict, waiter_rows=waiter_rows)

    # 4. Create print job
    if auto_print:
        payload = build_eod_payload(summary, waiter_rows, template_dict)
        job = await create_eod_print_job(db, tenant_id, payload)
        job_id = str(job.id)
    else:
        job_id = None

    return {
        "telegram_sent": telegram_sent,
        "print_job_id": job_id
    }
