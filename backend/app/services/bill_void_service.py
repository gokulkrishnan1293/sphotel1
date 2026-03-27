"""Bill void/unvoid lifecycle."""
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.bill_enums import BillStatus
from app.services.bill_service import _get_bill


async def void_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> Bill:
    bill = await _get_bill(db, tenant_id, bill_id)
    if bill.status == BillStatus.VOID:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bill is already void")
    bill.status = BillStatus.VOID
    await db.commit()
    await db.refresh(bill)
    return bill


async def unvoid_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> Bill:
    bill = await _get_bill(db, tenant_id, bill_id)
    if bill.status != BillStatus.VOID:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bill is not void")
    bill.status = BillStatus.BILLED if bill.paid_at else BillStatus.DRAFT
    await db.commit()
    await db.refresh(bill)
    return bill


async def cancel_bill(db: AsyncSession, tenant_id: str, bill_id: uuid.UUID) -> Bill:
    bill = await _get_bill(db, tenant_id, bill_id)
    if bill.status == BillStatus.BILLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot cancel a settled bill — use void instead")
    if bill.status in (BillStatus.CANCELLED, BillStatus.VOID):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Bill is already {bill.status}")
    bill.status = BillStatus.CANCELLED
    await db.commit()
    await db.refresh(bill)
    return bill
