import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import Section, TableLayout
from app.schemas.tables import SectionCreate, SectionUpdate, TableCreate, TableUpdate


# ── Section CRUD ────────────────────────────────────────────────────────────

async def list_sections(db: AsyncSession, tenant_id: str) -> Sequence[Section]:
    result = await db.execute(
        select(Section)
        .where(Section.tenant_id == tenant_id)
        .order_by(Section.position, Section.name)
    )
    return result.scalars().all()


async def get_section(db: AsyncSession, tenant_id: str, section_id: uuid.UUID) -> Section:
    result = await db.execute(
        select(Section).where(Section.id == section_id, Section.tenant_id == tenant_id)
    )
    section = result.scalar_one_or_none()
    if section is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return section


async def create_section(db: AsyncSession, tenant_id: str, data: SectionCreate) -> Section:
    section = Section(tenant_id=tenant_id, **data.model_dump())
    db.add(section)
    await db.commit()
    await db.refresh(section)
    return section


async def update_section(
    db: AsyncSession, tenant_id: str, section_id: uuid.UUID, data: SectionUpdate
) -> Section:
    section = await get_section(db, tenant_id, section_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    await db.commit()
    await db.refresh(section)
    return section


async def delete_section(db: AsyncSession, tenant_id: str, section_id: uuid.UUID) -> None:
    section = await get_section(db, tenant_id, section_id)
    await db.delete(section)
    await db.commit()


# ── Table CRUD ───────────────────────────────────────────────────────────────

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
        select(TableLayout).where(
            TableLayout.id == table_id, TableLayout.tenant_id == tenant_id
        )
    )
    table = result.scalar_one_or_none()
    if table is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


async def create_table(db: AsyncSession, tenant_id: str, data: TableCreate) -> TableLayout:
    # Verify section belongs to this tenant
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
