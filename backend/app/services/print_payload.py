"""Build receipt/KOT print payloads from bill data."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.bill_enums import ItemStatus
from app.models.kot import BillItem
from app.models.tenant import Tenant
from app.models.user import TenantUser
from app.schemas.print_template import PrintTemplateConfig


async def _fetch_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> Bill:
    r = await db.execute(select(Bill).where(Bill.id == bill_id, Bill.tenant_id == tenant_id))
    bill = r.scalar_one_or_none()
    if not bill:
        raise HTTPException(404, "Bill not found")
    return bill


async def _user_names(db: AsyncSession, tenant_id: str, *ids: uuid.UUID | None) -> dict:
    valid = [i for i in ids if i is not None]
    if not valid:
        return {}
    rows = await db.execute(
        select(TenantUser.id, TenantUser.name)
        .where(TenantUser.id.in_(valid), TenantUser.tenant_id == tenant_id)
    )
    return {r.id: r.name for r in rows}


async def _get_template(db: AsyncSession, tenant_id: str) -> dict:
    r = await db.execute(select(Tenant).where(Tenant.slug == tenant_id))
    tenant = r.scalar_one_or_none()
    if tenant and tenant.print_template:
        return PrintTemplateConfig(**tenant.print_template).model_dump()
    return PrintTemplateConfig().model_dump()


async def build_receipt_payload(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> dict:
    bill = await _fetch_bill(db, tenant_id, bill_id)
    items_r = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill_id, BillItem.status != ItemStatus.VOIDED)
    )
    items = items_r.scalars().all()
    template = await _get_template(db, tenant_id)
    names = await _user_names(db, tenant_id, bill.created_by, bill.waiter_id)
    return {
        "job_type": "receipt", "bill_id": str(bill_id),
        "bill_number": bill.bill_number, "bill_type": bill.bill_type,
        "table_id": str(bill.table_id) if bill.table_id else None,
        "reference_no": bill.reference_no, "platform": bill.platform,
        "cashier": names.get(bill.created_by),
        "waiter_name": names.get(bill.waiter_id) if bill.waiter_id else None,
        "customer_name": None,
        "items": [{"name": i.name, "qty": i.quantity, "price_paise": i.price_paise,
                   "special_note": getattr(i, "special_note", None), "food_type": i.food_type}
                  for i in items],
        "subtotal_paise": bill.subtotal_paise, "discount_paise": bill.discount_paise,
        "gst_paise": bill.gst_paise, "total_paise": bill.total_paise,
        "payment_method": bill.payment_method, "status": bill.status,
        "printed_at": datetime.now(tz=timezone.utc).isoformat(),
        "print_template": template,
    }


async def build_kot_payload(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID,
                             kot_number: int | None = None, include_pending: bool = False) -> dict:
    """Build KOT slip. include_pending=True for parcel/online where no prior KOT was fired."""
    bill = await _fetch_bill(db, tenant_id, bill_id)
    statuses = [ItemStatus.SENT, ItemStatus.PENDING] if include_pending else [ItemStatus.SENT]
    items_r = await db.execute(
        select(BillItem).where(BillItem.bill_id == bill_id, BillItem.status.in_(statuses))
    )
    items = items_r.scalars().all()
    template = await _get_template(db, tenant_id)
    return {
        "job_type": "kot",
        "bill_id": str(bill_id),
        "bill_number": getattr(bill, "bill_number", None),
        "kot_number": kot_number,
        "bill_type": bill.bill_type,
        "table_id": str(bill.table_id) if bill.table_id else None,
        "reference_no": bill.reference_no,
        "items": [{"name": i.name, "qty": i.quantity,
                   "special_note": getattr(i, "special_note", None)} for i in items],
        "printed_at": datetime.now(tz=timezone.utc).isoformat(),
        "print_template": template,
    }


def build_eod_payload(summary: dict, waiter_rows: list[dict], template: dict) -> dict:
    """Build EOD report payload. This does not require DB access."""
    return {
        "job_type": "eod_report",
        "printed_at": datetime.now(tz=timezone.utc).isoformat(),
        "print_template": template,
        "summary": summary,
        "waiter_rows": waiter_rows,
    }

