"""Bill item and KOT endpoints — Epic 4.2."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.bill_responses import BillItemResponse, KotTicketResponse
from app.schemas.bills import AddItemRequest, UpdateItemRequest
from app.schemas.common import DataResponse
from app.services import bill_item_service

router = APIRouter(prefix="/bills/{bill_id}", tags=["bill-items"])

_BILLING = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.post("/items", response_model=DataResponse[BillItemResponse], status_code=201)
async def add_item(
    bill_id: uuid.UUID,
    body: AddItemRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[BillItemResponse]:
    item = await bill_item_service.add_item(db, current_user["tenant_id"], bill_id, body)
    return DataResponse(data=BillItemResponse.model_validate(item))


@router.patch("/items/{item_id}", response_model=DataResponse[BillItemResponse])
async def update_item(
    bill_id: uuid.UUID,
    item_id: uuid.UUID,
    body: UpdateItemRequest,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[BillItemResponse]:
    item = await bill_item_service.update_item(db, current_user["tenant_id"], bill_id, item_id, body)
    return DataResponse(data=BillItemResponse.model_validate(item))


@router.delete("/items/{item_id}", status_code=204)
async def remove_item(
    bill_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> None:
    await bill_item_service.remove_item(db, current_user["tenant_id"], bill_id, item_id)


@router.post("/kot", response_model=DataResponse[KotTicketResponse], status_code=201)
async def fire_kot(
    bill_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[KotTicketResponse]:
    kot = await bill_item_service.fire_kot(db, current_user["tenant_id"], bill_id)
    return DataResponse(
        data=KotTicketResponse(id=kot.id, ticket_number=kot.ticket_number, fired_at=kot.fired_at)
    )
