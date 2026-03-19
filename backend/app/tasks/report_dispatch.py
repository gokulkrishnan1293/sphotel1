"""Dispatch scheduled reports as PDFs to Telegram."""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fixed_report_config import FixedReportConfig
from app.models.custom_report import CustomReport
from app.models.tenant import Tenant
from app.services.telegram_service import send_document_pdf

log = logging.getLogger("sphotel.tasks.dispatch")


async def dispatch_fixed_report(db: AsyncSession, cfg: FixedReportConfig, tenant: Tenant) -> bool:
    from app.services.analytics_service import daily_summary
    from app.services.analytics_query import waiter_performance
    from app.services.pdf_fixed import generate_top_items_pdf, generate_payment_pdf, generate_waiter_pdf

    assert tenant.telegram_bot_token and tenant.telegram_chat_id

    if cfg.report_type == "top_items":
        summary = await daily_summary(db, tenant.slug, date.today())
        items = summary.get("top_items", [])
        pdf = generate_top_items_pdf(items, tenant.name)
        filename = f"top_items_{tenant.slug}.pdf"
        caption = f"Top Items — {tenant.name}"

    elif cfg.report_type == "payment_breakdown":
        summary = await daily_summary(db, tenant.slug, date.today())
        breakdown = summary.get("payment_breakdown", {})
        pdf = generate_payment_pdf(breakdown, tenant.name)
        filename = f"payment_{tenant.slug}.pdf"
        caption = f"Payment Breakdown — {tenant.name}"

    elif cfg.report_type == "waiter_performance":
        rows = await waiter_performance(db, tenant.slug, days=7)
        pdf = generate_waiter_pdf(rows, tenant.name, days=7)
        filename = f"waiter_{tenant.slug}.pdf"
        caption = f"Waiter Performance — {tenant.name}"

    else:
        log.warning("Unknown fixed report type: %s", cfg.report_type)
        return False

    return await send_document_pdf(tenant.telegram_bot_token, tenant.telegram_chat_id,
                                   pdf, filename, caption)


async def dispatch_custom_report(db: AsyncSession, report: CustomReport, tenant: Tenant) -> bool:
    from app.services.analytics_query import run_custom_query
    from app.services.pdf_service import generate_custom_report_pdf

    assert tenant.telegram_bot_token and tenant.telegram_chat_id

    rows = await run_custom_query(db, tenant.slug, report.dimension or "date",
                                  report.metric, report.days)
    period = f"Last {report.days} days"
    pdf = generate_custom_report_pdf(report.name, period,
                                     report.dimension or "date", report.metric, rows)
    filename = f"{report.name.lower().replace(' ', '_')}_{tenant.slug}.pdf"
    caption = f"{report.name} — {tenant.name}"
    return await send_document_pdf(tenant.telegram_bot_token, tenant.telegram_chat_id,
                                   pdf, filename, caption)
