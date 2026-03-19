import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import TableLayout
from app.schemas.tables import TableCreate, TableUpdate
from app.services.section_service import get_section


async def list_tables(
    db: AsyncSession, tenant_id: str, section_id: uuid.UUID | None = None
) -> Sequence[TableLayout]:
    q = select(TableLayout).where(TableLayout.tenant_id == tenant_id)
    if section_id is not None:
        q = q.where(TableLayout.section_id == section_id)
    result = await db.execute(q.order_by(TableLayout.position, TableLayout.name))
    return result.scalars().all()


async def get_table(db: AsyncSession, tenant_id: str, table_id: uuid.UUID) -> TableLayout:
    result = await db.execute(
        select(TableLayout).where(TableLayout.id == table_id, TableLayout.tenant_id == tenant_id)
    )
    table = result.scalar_one_or_none()
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


async def create_table(db: AsyncSession, tenant_id: str, data: TableCreate) -> TableLayout:
    await get_section(db, tenant_id, data.section_id)
    table = TableLayout(tenant_id=tenant_id, **data.model_dump())
    db.add(table)
    await db.commit()
    await db.refresh(table)
    return table


async def update_table(
    db: AsyncSession, tenant_id: str, table_id: uuid.UUID, data: TableUpdate
) -> TableLayout:
    table = await get_table(db, tenant_id, table_id)
    if data.section_id is not None:
        await get_section(db, tenant_id, data.section_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(table, field, value)
    await db.commit()
    await db.refresh(table)
    return table


async def delete_table(db: AsyncSession, tenant_id: str, table_id: uuid.UUID) -> None:
    table = await get_table(db, tenant_id, table_id)
    await db.delete(table)
    await db.commit()
