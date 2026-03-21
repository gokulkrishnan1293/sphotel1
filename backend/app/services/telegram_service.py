"""Telegram Bot API integration for EOD reports and alerts."""
from __future__ import annotations

import logging
from datetime import date

import httpx
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import daily_summary

log = logging.getLogger("sphotel.telegram")

_API = "https://api.telegram.org/bot{token}/sendMessage"
_API_DOC = "https://api.telegram.org/bot{token}/sendDocument"


async def send_message(bot_token: str, chat_id: str, text_msg: str) -> bool:
    url = _API.format(token=bot_token)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json={"chat_id": chat_id, "text": text_msg, "parse_mode": "HTML"})
            return r.status_code == 200
    except Exception as exc:
        log.error("Telegram send failed: %s", exc)
        return False


async def send_document_pdf(bot_token: str, chat_id: str, pdf_bytes: bytes, filename: str, caption: str = "") -> bool:
    url = _API_DOC.format(token=bot_token)
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, data={"chat_id": chat_id, "caption": caption},
                                  files={"document": (filename, pdf_bytes, "application/pdf")})
            return r.status_code == 200
    except Exception as exc:
        log.error("Telegram PDF send failed: %s", exc)
        return False


def _fmt_inr(paise: int) -> str:
    return f"₹{paise / 100:,.0f}"


def format_eod(summary: dict, tenant_name: str, waiter_rows: list[dict] | None = None, template_flags: dict | None = None) -> str:
    flags = template_flags or {}
    show_payment = flags.get("eod_show_payment", True)
    show_items = flags.get("eod_show_items", True)
    show_waiters = flags.get("eod_show_waiters", True)

    lines = [
        f"<b>\ud83d\udcca EOD Report \u2014 {tenant_name}</b>",
        f"\ud83d\udcc5 {summary['date']}",
        "",
        f"\ud83e\uddfe Bills: <b>{summary['bill_count']}</b>",
        f"\ud83d\udcb0 Revenue: <b>{_fmt_inr(summary['total_paise'])}</b>",
        f"\ud83d\udcc9 Discounts: {_fmt_inr(summary['discount_paise'])}",
        f"\ud83e\uddfe Avg bill: {_fmt_inr(summary['avg_paise'])}",
        f"\ud83d\udeab Voids: {summary['void_count']}",
        "",
    ]
    if show_payment and summary.get("payment_breakdown"):
        lines.append("<b>Payment:</b>")
        for method, amt in summary["payment_breakdown"].items():
            lines.append(f"  {method}: {_fmt_inr(amt)}")
        lines.append("")
    if show_items and summary.get("top_items"):
        lines.append("<b>Top items:</b>")
        for item in summary["top_items"]:
            lines.append(f"  {item['name']} \u00d7 {item['qty']}")
        lines.append("")
    if show_waiters and waiter_rows:
        lines.append("<b>Waiters:</b>")
        for w in waiter_rows:
            lines.append(f"  {w['waiter_name']}: {_fmt_inr(w['revenue_paise'])}")
        lines.append("")
    return "\n".join(lines).strip()


async def send_eod_report(db: AsyncSession, tenant_id: str, tenant_name: str, for_date: date | None = None,
                          template: dict | None = None, waiter_rows: list[dict] | None = None) -> bool:
    from app.models.tenant import Tenant
    from app.services.pdf_service import generate_eod_pdf

    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant or not tenant.telegram_bot_token or not tenant.telegram_chat_id:
        return False

    summary = await daily_summary(db, tenant_id, for_date or date.today())
    msg = format_eod(summary, tenant_name or tenant.name, waiter_rows, template)
    
    # Send text format first (fallback/quick view)
    msg_ok = await send_message(tenant.telegram_bot_token, tenant.telegram_chat_id, msg)
    
    # Generate and send PDF
    pdf_bytes = generate_eod_pdf(summary, tenant_name or tenant.name, waiter_rows, template)
    date_str = (for_date or date.today()).strftime("%Y-%m-%d")
    fname = f"EOD_{tenant_name or tenant.name}_{date_str}.pdf".replace(" ", "_")
    
    await send_document_pdf(tenant.telegram_bot_token, tenant.telegram_chat_id, pdf_bytes, fname, caption="EOD Daily Report PDF")
    
    return msg_ok

async def set_telegram_webhook(bot_token: str, webhook_url: str) -> bool:
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json={"url": webhook_url})
            return r.status_code == 200
    except Exception as exc:
        log.error("Telegram setWebhook failed: %s", exc)
        return False

