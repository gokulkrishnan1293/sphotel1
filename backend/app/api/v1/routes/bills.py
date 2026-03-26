"""Bill CRUD endpoints — Epic 4.2."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import cast, select, String, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.bill import Bill
from app.models.bill_enums import BillStatus
from app.schemas.bill_responses import BillSummaryResponse
from app.schemas.bills import CloseBillRequest, OpenBillRequest, UpdatePaymentRequest
from app.schemas.common import DataResponse
from app.services import bill_service
from .bill_helpers import build_response, enrich_summaries, fetch_user_names

router = APIRouter(prefix="/bills", tags=["bills"])
_BILLING = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)

@router.get("/history", response_model=DataResponse[list[BillSummaryResponse]])
async def list_bill_history(
    q: str | None = None, status: str | None = None, limit: int = 50, offset: int = 0,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[BillSummaryResponse]]:
    statuses = [BillStatus.BILLED, BillStatus.VOID] if not status else [BillStatus(status)]
    stmt = select(Bill).where(Bill.tenant_id == current_user["tenant_id"], Bill.status.in_(statuses))
    if q: stmt = stmt.where(cast(Bill.bill_number, String).ilike(f'%{q}%'))
    r = await db.execute(stmt.order_by(Bill.updated_at.desc()).limit(limit).offset(offset))
    return DataResponse(data=await enrich_summaries(db, current_user["tenant_id"], list(r.scalars().all())))


@router.get("/recent", response_model=DataResponse[list[BillSummaryResponse]])
async def list_recent_bills(
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[BillSummaryResponse]]:
    r = await db.execute(select(Bill).where(Bill.tenant_id == current_user["tenant_id"], Bill.status.in_([BillStatus.BILLED, BillStatus.VOID])).order_by(Bill.updated_at.desc()).limit(30))
    return DataResponse(data=await enrich_summaries(db, current_user["tenant_id"], list(r.scalars().all())))


@router.get("", response_model=DataResponse[list[BillSummaryResponse]])
async def list_open_bills(
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[BillSummaryResponse]]:
    bills = list(await bill_service.list_open_bills(db, current_user["tenant_id"]))
    return DataResponse(data=await enrich_summaries(db, current_user["tenant_id"], bills))


@router.post("", response_model=DataResponse, status_code=201)
async def open_bill(
    body: OpenBillRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    bill = await bill_service.open_bill(db, current_user["tenant_id"], current_user["user_id"], body)
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill.id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.get("/{bill_id}", response_model=DataResponse)
async def get_bill(
    bill_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.post("/{bill_id}/close", response_model=DataResponse)
async def close_bill(
    bill_id: uuid.UUID, body: CloseBillRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    await bill_service.close_bill(db, current_user["tenant_id"], bill_id, body)
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))


@router.patch("/{bill_id}/payment-method", response_model=DataResponse)
async def update_payment_method(
    bill_id: uuid.UUID, body: UpdatePaymentRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    result = await db.execute(sa_update(Bill).where(Bill.id == bill_id, Bill.tenant_id == current_user["tenant_id"], Bill.status == BillStatus.BILLED).values(payment_method=body.payment_method).returning(Bill.id))
    if result.first() is None:
        raise HTTPException(400, "Bill not found or not in billed state")
    await db.commit()
    bill, items, kots = await bill_service.get_bill_with_items(db, current_user["tenant_id"], bill_id)
    names = await fetch_user_names(db, current_user["tenant_id"], bill.created_by, bill.waiter_id)
    return DataResponse(data=build_response(bill, items, kots, names))
