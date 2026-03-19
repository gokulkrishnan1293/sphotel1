import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse
from app.schemas.tables import TableCreate, TableResponse, TableUpdate
from app.services import table_layout_service

router = APIRouter(prefix="/tables/layouts", tags=["tables"])

_BILLING = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
_ADMIN = (UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("", response_model=DataResponse[list[TableResponse]])
async def list_tables(
    current_user: CurrentUser = Depends(require_role(*_BILLING)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[TableResponse]]:
    tables = await table_layout_service.list_tables(db, current_user["tenant_id"])
    return DataResponse(data=[TableResponse.model_validate(t) for t in tables])


@router.post("", response_model=DataResponse[TableResponse], status_code=201)
async def create_table(
    body: TableCreate,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TableResponse]:
    table = await table_layout_service.create_table(db, current_user["tenant_id"], body)
    return DataResponse(data=TableResponse.model_validate(table))


@router.patch("/{table_id}", response_model=DataResponse[TableResponse])
async def update_table(
    table_id: uuid.UUID,
    body: TableUpdate,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TableResponse]:
    table = await table_layout_service.update_table(db, current_user["tenant_id"], table_id, body)
    return DataResponse(data=TableResponse.model_validate(table))


@router.delete("/{table_id}", status_code=204)
async def delete_table(
    table_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> None:
    await table_layout_service.delete_table(db, current_user["tenant_id"], table_id)
