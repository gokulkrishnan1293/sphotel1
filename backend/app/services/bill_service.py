"""Core bill lifecycle — open, list, get, close, void."""

import uuid
from datetime import date, datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.bill_enums import BillStatus
from app.models.kot import BillItem, KotTicket
from app.schemas.bills import CloseBillRequest, OpenBillRequest


async def _get_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> Bill:
    result = await db.execute(
        select(Bill).where(Bill.id == bill_id, Bill.tenant_id == tenant_id)
    )
    bill = result.scalar_one_or_none()
    if bill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    return bill


def assert_active(bill: Bill) -> None:
    if bill.status in (BillStatus.BILLED, BillStatus.VOID):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bill is already {bill.status}",
        )


async def recalc_totals(db: AsyncSession, bill: Bill) -> None:
    from app.models.bill_enums import ItemStatus
    eff_price = func.coalesce(BillItem.override_price_paise, BillItem.price_paise)
    result = await db.execute(
        select(func.coalesce(func.sum(eff_price * BillItem.quantity), 0)).where(
            BillItem.bill_id == bill.id,
            BillItem.status.in_([ItemStatus.PENDING, ItemStatus.SENT]),
        )
    )
    subtotal = int(result.scalar_one())
    bill.subtotal_paise = subtotal
    bill.total_paise = max(0, subtotal - bill.discount_paise + bill.gst_paise)


async def open_bill(
    db: AsyncSession, tenant_id: str, created_by: uuid.UUID, data: OpenBillRequest
) -> Bill:
    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
    max_num = (await db.execute(
        select(func.coalesce(func.max(Bill.bill_number), 0)).where(
            Bill.tenant_id == tenant_id, Bill.created_at >= today_start
        )
    )).scalar_one()
    bill = Bill(tenant_id=tenant_id, created_by=created_by, bill_number=int(max_num) + 1, **data.model_dump())
    db.add(bill)
    await db.commit()
    await db.refresh(bill)
    return bill


async def list_open_bills(db: AsyncSession, tenant_id: str) -> Sequence[Bill]:
    result = await db.execute(
        select(Bill)
        .where(Bill.tenant_id == tenant_id, Bill.status.notin_([BillStatus.BILLED, BillStatus.VOID]))
        .order_by(Bill.created_at)
    )
    return result.scalars().all()


async def get_bill_with_items(
    db: AsyncSession, tenant_id: str, bill_id: uuid.UUID
) -> tuple[Bill, Sequence[BillItem], Sequence[KotTicket]]:
    bill = await _get_bill(db, tenant_id, bill_id)
    items = (await db.execute(
        select(BillItem).where(BillItem.bill_id == bill_id).order_by(BillItem.created_at)
    )).scalars().all()
    kots = (await db.execute(
        select(KotTicket).where(KotTicket.bill_id == bill_id).order_by(KotTicket.fired_at)
    )).scalars().all()
    return bill, items, kots


async def close_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID, data: CloseBillRequest) -> Bill:
    from datetime import datetime, timezone
    bill = await _get_bill(db, tenant_id, bill_id)
    assert_active(bill)
    bill.discount_paise = data.discount_paise
    await recalc_totals(db, bill)
    bill.payment_method = data.payment_method
    bill.paid_at = datetime.now(tz=timezone.utc)
    bill.status = BillStatus.BILLED
    await db.commit()
    await db.refresh(bill)
    return bill
