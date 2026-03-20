"""Per-tenant keyboard shortcut configuration."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.tenant import Tenant
from app.schemas.common import DataResponse

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
_DEFAULTS = {
    "open_search": "Space",
    "fire_kot": "ctrl+k",
    "generate_bill": "g",
    "close_bill": "Enter",
    "new_bill": "n",
}

router = APIRouter(prefix="/keyboard-shortcuts", tags=["keyboard-shortcuts"])


class ShortcutPatch(BaseModel):
    open_search: str | None = None
    fire_kot: str | None = None
    generate_bill: str | None = None
    close_bill: str | None = None
    new_bill: str | None = None


async def _tenant(db: AsyncSession, tenant_id: str) -> Tenant:
    t = (await db.execute(select(Tenant).where(Tenant.slug == tenant_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return t


@router.get("")
async def get_shortcuts(db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    tenant = await _tenant(db, cu["tenant_id"])
    return DataResponse(data={**_DEFAULTS, **(tenant.keyboard_shortcuts or {})})


@router.patch("")
async def update_shortcuts(
    body: ShortcutPatch,
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    tenant = await _tenant(db, cu["tenant_id"])
    current = {**_DEFAULTS, **(tenant.keyboard_shortcuts or {})}
    new_shortcuts = {**current, **body.model_dump(exclude_none=True)}
    tenant.keyboard_shortcuts = new_shortcuts
    await db.commit()
    return DataResponse(data=new_shortcuts)
