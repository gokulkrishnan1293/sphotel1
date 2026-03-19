"""Background task: fires scheduled reports based on per-card cron expressions."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from croniter import croniter
from sqlalchemy import select

log = logging.getLogger("sphotel.tasks.eod")
_IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> datetime:
    return datetime.now(_IST).replace(second=0, microsecond=0)


def _matches(expr: str, now: datetime) -> bool:
    try:
        return croniter.match(expr, now)
    except Exception:
        return False


async def _tick(now: datetime) -> None:
    from app.db.session import async_session_maker
    from app.models.tenant import Tenant
    from app.models.fixed_report_config import FixedReportConfig
    from app.models.custom_report import CustomReport
    from app.tasks.report_dispatch import dispatch_fixed_report, dispatch_custom_report
    from app.repositories.feature_flags import get_feature_flags_from_db

    async with async_session_maker() as db:
        fixed = (await db.execute(
            select(FixedReportConfig).where(FixedReportConfig.telegram_schedule.is_not(None))
        )).scalars().all()
        custom = (await db.execute(
            select(CustomReport).where(CustomReport.telegram_schedule.is_not(None))
        )).scalars().all()

    for cfg in fixed:
        if not _matches(cfg.telegram_schedule, now):  # type: ignore[arg-type]
            continue
        try:
            async with async_session_maker() as db:
                tenant = (await db.execute(
                    select(Tenant).where(Tenant.slug == cfg.tenant_id, Tenant.is_active.is_(True))
                )).scalar_one_or_none()
                if not tenant or not tenant.telegram_bot_token or not tenant.telegram_chat_id:
                    continue
                flags = await get_feature_flags_from_db(tenant.id, db)
                if not flags["telegram_alerts"]:
                    continue
                ok = await dispatch_fixed_report(db, cfg, tenant)
                log.info("Fixed report %s/%s %s", cfg.tenant_id, cfg.report_type, "sent" if ok else "failed")
        except Exception as exc:
            log.error("Fixed report error %s/%s: %s", cfg.tenant_id, cfg.report_type, exc)

    for report in custom:
        if not _matches(report.telegram_schedule, now):  # type: ignore[arg-type]
            continue
        try:
            async with async_session_maker() as db:
                tenant = (await db.execute(
                    select(Tenant).where(Tenant.slug == report.tenant_id, Tenant.is_active.is_(True))
                )).scalar_one_or_none()
                if not tenant or not tenant.telegram_bot_token or not tenant.telegram_chat_id:
                    continue
                flags = await get_feature_flags_from_db(tenant.id, db)
                if not flags["telegram_alerts"]:
                    continue
                ok = await dispatch_custom_report(db, report, tenant)
                log.info("Custom report %s/%s %s", report.tenant_id, report.name, "sent" if ok else "failed")
        except Exception as exc:
            log.error("Custom report error %s/%s: %s", report.tenant_id, report.name, exc)


async def eod_scheduler() -> None:
    log.info("Cron scheduler started")
    while True:
        now = _now_ist()
        next_min = now + timedelta(minutes=1)
        sleep_secs = (next_min - datetime.now(_IST)).total_seconds()
        await asyncio.sleep(max(sleep_secs, 1))
        await _tick(_now_ist())
