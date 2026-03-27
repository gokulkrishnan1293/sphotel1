"""Bill void/unvoid/cancel action endpoints."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.bill import Bill
from app.models.bill_enums import BillStatus
from app.schemas.bills import UpdateBillRequest
from app.schemas.common import DataResponse
from app.services import bill_service, bill_void_service
from app.api.v1.routes.bill_helpers import build_response, fetch_user_names

router = APIRouter(prefix="/bills", tags=["bills"])
_BILLING = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
_CLOSED = [BillStatus.BILLED, BillStatus.VOID, BillStatus.CANCELLED]


@router.patch("/{bill_id}", response_model=DataResponse)
async def update_bill(
    bill_id: uuid.UUID, body: UpdateBillRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    values = body.model_dump(exclude_unset=True)
    if values:
        result = await db.execute(sa_update(Bill).where(Bill.id == bill_id, Bill.tenant_id == current_user["tenant_id"], Bill.status.not_in(_CLOSED)).values(**values).returning(Bill.id))
        if result.first() is None:
            raise HTTPException(400, "Bill not found or already closed")
        await db.commit()
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.post("/{bill_id}/void", response_model=DataResponse)
async def void_bill(
    bill_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    await bill_void_service.void_bill(db, current_user["tenant_id"], bill_id)
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.post("/{bill_id}/unvoid", response_model=DataResponse)
async def unvoid_bill(
    bill_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    await bill_void_service.unvoid_bill(db, current_user["tenant_id"], bill_id)
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.post("/{bill_id}/cancel", response_model=DataResponse)
async def cancel_bill(
    bill_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    await bill_void_service.cancel_bill(db, current_user["tenant_id"], bill_id)
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))
