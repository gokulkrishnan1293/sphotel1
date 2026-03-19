"""Bill item and KOT operations."""

import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill_enums import BillStatus, ItemStatus
from app.models.kot import BillItem, KotTicket
from app.schemas.bills import AddItemRequest, UpdateItemRequest
from app.services.bill_service import _get_bill, assert_active, recalc_totals


async def add_item(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID, data: AddItemRequest) -> BillItem:
    bill = await _get_bill(db, tenant_id, bill_id)
    assert_active(bill)
    if data.menu_item_id:
        ex = (await db.execute(select(BillItem).where(
            BillItem.bill_id == bill_id, BillItem.menu_item_id == data.menu_item_id,
            BillItem.name == data.name, BillItem.status == ItemStatus.PENDING,
        ))).scalar_one_or_none()
        if ex:
            ex.quantity += data.quantity
            await recalc_totals(db, bill); await db.commit(); await db.refresh(ex); return ex
    item = BillItem(tenant_id=tenant_id, bill_id=bill_id, **data.model_dump())
    db.add(item)
    if bill.status == BillStatus.KOT_SENT:
        bill.status = BillStatus.PARTIALLY_SENT
    await db.flush()
    await recalc_totals(db, bill); await db.commit(); await db.refresh(item); return item


async def update_item(
    db: AsyncSession, tenant_id: str, bill_id: uuid.UUID, item_id: uuid.UUID, data: UpdateItemRequest
) -> BillItem:
    bill = await _get_bill(db, tenant_id, bill_id)
    assert_active(bill)
    result = await db.execute(
        select(BillItem).where(BillItem.id == item_id, BillItem.bill_id == bill_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.status == ItemStatus.VOIDED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot modify voided item")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await recalc_totals(db, bill)
    await db.commit()
    await db.refresh(item)
    return item


async def remove_item(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID, item_id: uuid.UUID) -> None:
    bill = await _get_bill(db, tenant_id, bill_id)
    assert_active(bill)
    result = await db.execute(
        select(BillItem).where(BillItem.id == item_id, BillItem.bill_id == bill_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.status == ItemStatus.SENT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot remove a sent item. Use void request.",
        )
    await db.delete(item)
    await recalc_totals(db, bill)
    await db.commit()


async def fire_kot(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> KotTicket:
    bill = await _get_bill(db, tenant_id, bill_id)
    assert_active(bill)
    pending = (await db.execute(
        select(BillItem).where(BillItem.bill_id == bill_id, BillItem.status == ItemStatus.PENDING)
    )).scalars().all()
    if not pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No pending items to fire")

    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
    max_num = (await db.execute(
        select(func.coalesce(func.max(KotTicket.ticket_number), 0)).where(
            KotTicket.tenant_id == tenant_id, KotTicket.fired_at >= today_start
        )
    )).scalar_one()
    kot = KotTicket(tenant_id=tenant_id, bill_id=bill_id, ticket_number=int(max_num) + 1)
    db.add(kot)
    await db.flush()
    for item in pending:
        item.status = ItemStatus.SENT
        item.kot_ticket_id = kot.id
    bill.status = BillStatus.KOT_SENT
    await db.commit()
    await db.refresh(kot)
    return kot
