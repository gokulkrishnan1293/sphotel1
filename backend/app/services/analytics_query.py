"""Whitelist-based dynamic analytics queries."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_DIMS: dict[str, dict] = {
    "waiter": {"sel": "COALESCE(tu.name,'No Waiter')", "join": "LEFT JOIN tenant_users tu ON b.waiter_id=tu.id AND tu.tenant_id=:tid"},
    "table": {"sel": "COALESCE(tl.name,'No Table')", "join": "LEFT JOIN table_layouts tl ON b.table_id=tl.id"},
    "payment_method": {"sel": "COALESCE(b.payment_method::text,'unknown')", "join": ""},
    "category": {"sel": "bi.category", "join": "JOIN bill_items bi ON bi.bill_id=b.id AND bi.status!='voided'"},
    "item": {"sel": "bi.name", "join": "JOIN bill_items bi ON bi.bill_id=b.id AND bi.status!='voided'"},
    "date": {"sel": "DATE(b.paid_at AT TIME ZONE 'Asia/Kolkata')::text", "join": ""},
    "hour": {"sel": "EXTRACT(HOUR FROM b.paid_at AT TIME ZONE 'Asia/Kolkata')::int::text", "join": ""},
}
_METS: dict[str, str] = {
    "revenue": "SUM(b.total_paise)",
    "bill_count": "COUNT(DISTINCT b.id)",
    "avg_bill": "AVG(b.total_paise)::bigint",
    "item_qty": "SUM(bi.quantity)",
}


async def waiter_performance(db: AsyncSession, tenant_id: str, days: int = 7) -> list[dict]:
    rows = await db.execute(text("""
        SELECT COALESCE(tu.name, 'No Waiter') AS waiter_name,
            COUNT(DISTINCT b.id) AS bill_count,
            SUM(b.total_paise) AS revenue_paise
        FROM bills b
        LEFT JOIN tenant_users tu ON b.waiter_id = tu.id AND tu.tenant_id = :tid
        WHERE b.tenant_id = :tid AND b.status = 'billed'
          AND b.paid_at >= NOW() - make_interval(days => :days)
        GROUP BY tu.name ORDER BY revenue_paise DESC LIMIT 10
    """), {"tid": tenant_id, "days": days})
    return [{"waiter_name": r["waiter_name"], "bill_count": int(r["bill_count"]), "revenue_paise": int(r["revenue_paise"])}
            for r in rows.mappings()]


async def run_custom_query(db: AsyncSession, tenant_id: str, dimension: str, metric: str, days: int) -> list[dict]:
    dim = _DIMS.get(dimension)
    met = _METS.get(metric)
    if not dim or not met:
        return []
    join = dim["join"]
    if metric == "item_qty" and "bill_items" not in join:
        join += " JOIN bill_items bi ON bi.bill_id=b.id AND bi.status!='voided'"
    sql = f"""SELECT {dim["sel"]} AS label, {met} AS value
        FROM bills b {join}
        WHERE b.tenant_id = :tid AND b.status = 'billed'
          AND b.paid_at >= NOW() - make_interval(days => :days)
        GROUP BY {dim["sel"]} ORDER BY value DESC NULLS LAST LIMIT 20"""
    rows = await db.execute(text(sql), {"tid": tenant_id, "days": days})
    return [{"label": str(r["label"] or "Unknown"), "value": int(r["value"] or 0)} for r in rows.mappings()]
