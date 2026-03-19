"""KOT action endpoints — mark ready."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.kot import KotTicket
from app.schemas.common import DataResponse

router = APIRouter(prefix="/kot", tags=["kot"])

_ALLOWED = require_role(
    UserRole.KITCHEN_STAFF, UserRole.BILLER, UserRole.MANAGER,
    UserRole.ADMIN, UserRole.SUPER_ADMIN,
)


@router.post("/{kot_id}/ready", response_model=DataResponse[dict])
async def mark_kot_ready(
    kot_id: uuid.UUID,
    user: CurrentUser = Depends(_ALLOWED),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[dict]:
    """Mark a KOT as ready — removes it from the kitchen display."""
    res = await db.execute(
        select(KotTicket).where(
            KotTicket.id == kot_id,
            KotTicket.tenant_id == user["tenant_id"],
        )
    )
    kot = res.scalar_one_or_none()
    if not kot:
        raise HTTPException(status_code=404, detail="KOT not found")
    kot.ready_at = datetime.now(tz=timezone.utc)
    await db.commit()
    return DataResponse(data={"id": str(kot_id), "ready": True})


@router.post("/{kot_id}/items/{item_id}/ready", response_model=DataResponse[list[str]])
async def toggle_item_ready(
    kot_id: uuid.UUID,
    item_id: uuid.UUID,
    user: CurrentUser = Depends(_ALLOWED),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[str]]:
    """Toggle per-item readiness on a KOT — persists across devices."""
    res = await db.execute(
        select(KotTicket).where(KotTicket.id == kot_id, KotTicket.tenant_id == user["tenant_id"])
    )
    kot = res.scalar_one_or_none()
    if not kot:
        raise HTTPException(status_code=404, detail="KOT not found")
    ids: list[str] = list(kot.ready_item_ids or [])
    sid = str(item_id)
    if sid in ids:
        ids.remove(sid)
    else:
        ids.append(sid)
    kot.ready_item_ids = ids
    await db.commit()
    return DataResponse(data=ids)
