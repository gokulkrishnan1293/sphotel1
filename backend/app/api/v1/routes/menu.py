import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.menu import MenuItem
from app.schemas.common import DataResponse, MessageResponse
from app.schemas.menu import CategoryRename, CategoryResponse, MenuItemCreate, MenuItemResponse, MenuItemUpdate
from app.services import menu_service
from app.services.menu_csv import export_csv, import_csv

router = APIRouter(prefix="/menu", tags=["menu"])
_ADMIN = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)


@router.get("/items", response_model=DataResponse[list[MenuItemResponse]])
async def list_items(cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[list[MenuItemResponse]]:
    items = await menu_service.list_menu_items(db, cu["tenant_id"])
    return DataResponse(data=[MenuItemResponse.model_validate(i) for i in items])


@router.post("/items", response_model=DataResponse[MenuItemResponse], status_code=201)
async def create_item(body: MenuItemCreate, cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[MenuItemResponse]:
    item = await menu_service.create_menu_item(db, cu["tenant_id"], body)
    return DataResponse(data=MenuItemResponse.model_validate(item))


@router.patch("/items/{item_id}", response_model=DataResponse[MenuItemResponse])
async def update_item(item_id: uuid.UUID, body: MenuItemUpdate, cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[MenuItemResponse]:
    item = await menu_service.update_menu_item(db, cu["tenant_id"], item_id, body)
    return DataResponse(data=MenuItemResponse.model_validate(item))


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: uuid.UUID, cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> None:
    await menu_service.delete_menu_item(db, cu["tenant_id"], item_id)


@router.get("/export", response_class=PlainTextResponse)
async def export_items(cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> PlainTextResponse:
    items = await menu_service.list_menu_items(db, cu["tenant_id"])
    csv_text = export_csv(items)
    return PlainTextResponse(csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=menu.csv"})


@router.post("/import", response_model=DataResponse[dict])
async def import_items(file: UploadFile = File(...), cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[dict]:
    content = (await file.read()).decode("utf-8")
    result = await import_csv(db, cu["tenant_id"], content)
    return DataResponse(data=result)


@router.get("/categories", response_model=DataResponse[list[CategoryResponse]])
async def list_categories(cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[list[CategoryResponse]]:
    result = await db.execute(
        select(MenuItem.category, func.count(MenuItem.id).label("count"))
        .where(MenuItem.tenant_id == cu["tenant_id"]).group_by(MenuItem.category).order_by(MenuItem.category)
    )
    return DataResponse(data=[CategoryResponse(name=r.category, item_count=r.count) for r in result.all()])


@router.patch("/categories/{old_name}", response_model=DataResponse[MessageResponse])
async def rename_category(old_name: str, body: CategoryRename, cu: CurrentUser = Depends(_ADMIN), db: AsyncSession = Depends(get_db)) -> DataResponse[MessageResponse]:
    await db.execute(update(MenuItem).where(MenuItem.tenant_id == cu["tenant_id"], MenuItem.category == old_name).values(category=body.new_name))
    await db.commit()
    return DataResponse(data=MessageResponse(message=f"Renamed to '{body.new_name}'"))
