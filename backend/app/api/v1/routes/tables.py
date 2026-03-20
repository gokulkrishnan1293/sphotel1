import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse, MessageResponse
from app.schemas.tables import (
    SectionCreate,
    SectionResponse,
    SectionUpdate,
    SectionWithTablesResponse,
    TableCreate,
    TableResponse,
    TableUpdate,
)
from app.services import table_service

router = APIRouter(prefix="/tables", tags=["tables"])

# ── Sections ─────────────────────────────────────────────────────────────────

@router.get("/sections", response_model=DataResponse[list[SectionWithTablesResponse]])
async def list_sections(
    current_user: CurrentUser = Depends(require_role(UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[SectionWithTablesResponse]]:
    sections = await table_service.list_sections(db, current_user["tenant_id"])
    tables = await table_service.list_tables(db, current_user["tenant_id"])

    # Group tables by section
    tables_by_section: dict[uuid.UUID, list] = {}
    for t in tables:
        tables_by_section.setdefault(t.section_id, []).append(t)

    result = []
    for s in sections:
        s_resp = SectionWithTablesResponse.model_validate(s)
        s_resp.tables = [TableResponse.model_validate(t) for t in tables_by_section.get(s.id, [])]
        result.append(s_resp)

    return DataResponse(data=result)


@router.post("/sections", response_model=DataResponse[SectionResponse], status_code=201)
async def create_section(
    body: SectionCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[SectionResponse]:
    section = await table_service.create_section(db, current_user["tenant_id"], body)
    return DataResponse(data=SectionResponse.model_validate(section))


@router.patch("/sections/{section_id}", response_model=DataResponse[SectionResponse])
async def update_section(
    section_id: uuid.UUID,
    body: SectionUpdate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[SectionResponse]:
    section = await table_service.update_section(db, current_user["tenant_id"], section_id, body)
    return DataResponse(data=SectionResponse.model_validate(section))


@router.delete("/sections/{section_id}", status_code=204)
async def delete_section(
    section_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> None:
    await table_service.delete_section(db, current_user["tenant_id"], section_id)


# ── Tables ────────────────────────────────────────────────────────────────────

@router.get("/layouts", response_model=DataResponse[list[TableResponse]])
async def list_tables(
    current_user: CurrentUser = Depends(
        require_role(UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
    ),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[TableResponse]]:
    tables = await table_service.list_tables(db, current_user["tenant_id"])
    return DataResponse(data=[TableResponse.model_validate(t) for t in tables])


@router.post("/layouts", response_model=DataResponse[TableResponse], status_code=201)
async def create_table(
    body: TableCreate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TableResponse]:
    table = await table_service.create_table(db, current_user["tenant_id"], body)
    return DataResponse(data=TableResponse.model_validate(table))


@router.patch("/layouts/{table_id}", response_model=DataResponse[TableResponse])
async def update_table(
    table_id: uuid.UUID,
    body: TableUpdate,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[TableResponse]:
    table = await table_service.update_table(db, current_user["tenant_id"], table_id, body)
    return DataResponse(data=TableResponse.model_validate(table))


@router.delete("/layouts/{table_id}", status_code=204)
async def delete_table(
    table_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> None:
    await table_service.delete_table(db, current_user["tenant_id"], table_id)
