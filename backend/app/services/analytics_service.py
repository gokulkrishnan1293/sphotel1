"""Analytics queries for reports and Telegram EOD summaries."""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def daily_summary(db: AsyncSession, tenant_id: str, for_date: date) -> dict:
    rows = await db.execute(text("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'billed') AS bill_count,
            COALESCE(SUM(total_paise) FILTER (WHERE status = 'billed'), 0) AS total_paise,
            COALESCE(SUM(discount_paise) FILTER (WHERE status = 'billed'), 0) AS discount_paise,
            COUNT(*) FILTER (WHERE status = 'void') AS void_count,
            payment_method
        FROM bills
        WHERE tenant_id = :tid
          AND DATE(COALESCE(paid_at, updated_at) AT TIME ZONE 'Asia/Kolkata') = :d
          AND status IN ('billed', 'void')
        GROUP BY payment_method
    """), {"tid": tenant_id, "d": for_date})
    payment_rows = rows.mappings().all()

    bill_count = sum(r["bill_count"] for r in payment_rows)
    total_paise = sum(r["total_paise"] for r in payment_rows)
    discount_paise = sum(r["discount_paise"] for r in payment_rows)
    void_count = sum(r["void_count"] for r in payment_rows)
    avg_paise = (total_paise // bill_count) if bill_count else 0
    payment_breakdown = {r["payment_method"]: int(r["total_paise"]) for r in payment_rows if r["payment_method"]}

    items = await db.execute(text("""
        SELECT bi.name, SUM(bi.quantity) AS qty
        FROM bill_items bi JOIN bills b ON bi.bill_id = b.id
        WHERE b.tenant_id = :tid AND b.status = 'billed'
          AND DATE(b.paid_at AT TIME ZONE 'Asia/Kolkata') = :d
          AND bi.status != 'voided'
        GROUP BY bi.name ORDER BY qty DESC LIMIT 5
    """), {"tid": tenant_id, "d": for_date})
    top_items = [{"name": r["name"], "qty": int(r["qty"])} for r in items.mappings()]

    return {"date": str(for_date), "bill_count": bill_count, "total_paise": total_paise,
            "avg_paise": avg_paise, "discount_paise": discount_paise,
            "void_count": void_count, "payment_breakdown": payment_breakdown, "top_items": top_items}


async def hourly_heatmap(db: AsyncSession, tenant_id: str, days: int = 28) -> list[dict]:
    rows = await db.execute(text("""
        SELECT
            EXTRACT(DOW FROM paid_at AT TIME ZONE 'Asia/Kolkata')::int AS dow,
            EXTRACT(HOUR FROM paid_at AT TIME ZONE 'Asia/Kolkata')::int AS hour,
            SUM(total_paise) AS total_paise, COUNT(*) AS count
        FROM bills
        WHERE tenant_id = :tid AND status = 'billed'
          AND paid_at >= NOW() - make_interval(days => :days)
        GROUP BY dow, hour ORDER BY dow, hour
    """), {"tid": tenant_id, "days": days})
    return [{"dow": r["dow"], "hour": r["hour"], "total_paise": int(r["total_paise"]), "count": int(r["count"])}
            for r in rows.mappings()]


async def item_velocity(db: AsyncSession, tenant_id: str, days: int = 14) -> list[dict]:
    rows = await db.execute(text("""
        SELECT bi.name,
            COALESCE(SUM(bi.quantity) FILTER (WHERE b.paid_at >= NOW() - '7 days'::interval), 0) AS this_week,
            COALESCE(SUM(bi.quantity) FILTER (WHERE b.paid_at < NOW() - '7 days'::interval), 0) AS last_week
        FROM bill_items bi JOIN bills b ON bi.bill_id = b.id
        WHERE b.tenant_id = :tid AND b.status = 'billed'
          AND b.paid_at >= NOW() - make_interval(days => :days) AND bi.status != 'voided'
        GROUP BY bi.name ORDER BY this_week DESC LIMIT 20
    """), {"tid": tenant_id, "days": days})
    result = []
    for r in rows.mappings():
        tw, lw = int(r["this_week"]), int(r["last_week"])
        change = round((tw - lw) / lw * 100) if lw else None
        result.append({"name": r["name"], "this_week": tw, "last_week": lw, "change_pct": change})
    return result


async def table_turns(db: AsyncSession, tenant_id: str, days: int = 7) -> list[dict]:
    rows = await db.execute(text("""
        SELECT tl.name AS table_name, COUNT(*) AS turn_count,
            ROUND(AVG(EXTRACT(EPOCH FROM (b.paid_at - b.created_at)) / 60)) AS avg_minutes
        FROM bills b JOIN table_layouts tl ON b.table_id = tl.id
        WHERE b.tenant_id = :tid AND b.status = 'billed' AND b.table_id IS NOT NULL
          AND b.paid_at >= NOW() - make_interval(days => :days)
        GROUP BY tl.name ORDER BY avg_minutes DESC
    """), {"tid": tenant_id, "days": days})
    return [{"table_name": r["table_name"], "turn_count": int(r["turn_count"]), "avg_minutes": int(r["avg_minutes"])}
            for r in rows.mappings()]
