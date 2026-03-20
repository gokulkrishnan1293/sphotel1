import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse
from app.schemas.tables import SectionCreate, SectionResponse, SectionUpdate, SectionWithTablesResponse, TableResponse
from app.services import section_service, table_layout_service

router = APIRouter(prefix="/tables/sections", tags=["tables"])

_ADMIN = (UserRole.ADMIN, UserRole.SUPER_ADMIN)
_READ = (UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("", response_model=DataResponse[list[SectionWithTablesResponse]])
async def list_sections(
    current_user: CurrentUser = Depends(require_role(*_READ)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[SectionWithTablesResponse]]:
    sections = await section_service.list_sections(db, current_user["tenant_id"])
    tables = await table_layout_service.list_tables(db, current_user["tenant_id"])
    tbl_map: dict[uuid.UUID, list] = {}
    for t in tables:
        tbl_map.setdefault(t.section_id, []).append(t)
    result = []
    for s in sections:
        resp = SectionWithTablesResponse.model_validate(s)
        resp.tables = [TableResponse.model_validate(t) for t in tbl_map.get(s.id, [])]
        result.append(resp)
    return DataResponse(data=result)


@router.post("", response_model=DataResponse[SectionResponse], status_code=201)
async def create_section(
    body: SectionCreate,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[SectionResponse]:
    section = await section_service.create_section(db, current_user["tenant_id"], body)
    return DataResponse(data=SectionResponse.model_validate(section))


@router.patch("/{section_id}", response_model=DataResponse[SectionResponse])
async def update_section(
    section_id: uuid.UUID,
    body: SectionUpdate,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[SectionResponse]:
    section = await section_service.update_section(db, current_user["tenant_id"], section_id, body)
    return DataResponse(data=SectionResponse.model_validate(section))


@router.delete("/{section_id}", status_code=204)
async def delete_section(
    section_id: uuid.UUID,
    current_user: CurrentUser = Depends(require_role(*_ADMIN)),
    db: AsyncSession = Depends(get_db),
) -> None:
    await section_service.delete_section(db, current_user["tenant_id"], section_id)
