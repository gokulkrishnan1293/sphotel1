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


def format_eod(summary: dict, tenant_name: str) -> str:
    lines = [
        f"<b>📊 EOD Report — {tenant_name}</b>",
        f"📅 {summary['date']}",
        "",
        f"🧾 Bills: <b>{summary['bill_count']}</b>",
        f"💰 Revenue: <b>{_fmt_inr(summary['total_paise'])}</b>",
        f"📉 Discounts: {_fmt_inr(summary['discount_paise'])}",
        f"🧾 Avg bill: {_fmt_inr(summary['avg_paise'])}",
        f"🚫 Voids: {summary['void_count']}",
        "",
    ]
    if summary.get("payment_breakdown"):
        lines.append("<b>Payment:</b>")
        for method, amt in summary["payment_breakdown"].items():
            lines.append(f"  {method}: {_fmt_inr(amt)}")
        lines.append("")
    if summary.get("top_items"):
        lines.append("<b>Top items:</b>")
        for item in summary["top_items"]:
            lines.append(f"  {item['name']} × {item['qty']}")
    return "\n".join(lines)


async def send_eod_report(db: AsyncSession, tenant_id: str, tenant_name: str, for_date: date | None = None) -> bool:
    from app.models.tenant import Tenant
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant or not tenant.telegram_bot_token or not tenant.telegram_chat_id:
        return False
    summary = await daily_summary(db, tenant_id, for_date or date.today())
    msg = format_eod(summary, tenant_name or tenant.name)
    return await send_message(tenant.telegram_bot_token, tenant.telegram_chat_id, msg)
