"""Bill void/unvoid action endpoints."""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse
from app.services import bill_service, bill_void_service
from app.api.v1.routes.bill_helpers import build_response, fetch_user_names

router = APIRouter(prefix="/bills", tags=["bills"])
_BILLING = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)


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
