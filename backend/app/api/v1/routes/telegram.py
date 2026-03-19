"""Telegram settings and manual EOD trigger."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.schemas.common import DataResponse

_AUTH = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)
from app.models.tenant import Tenant
from app.services.telegram_service import send_eod_report, send_message

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramSettings(BaseModel):
    bot_token: str | None = None
    chat_id: str | None = None


async def _get_tenant(db: AsyncSession, tenant_id: str) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.slug == tenant_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return t


@router.get("/settings")
async def get_settings(db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    tenant = await _get_tenant(db, cu["tenant_id"])
    return DataResponse(data={"bot_token": tenant.telegram_bot_token, "chat_id": tenant.telegram_chat_id})


@router.patch("/settings")
async def update_settings(
    body: TelegramSettings,
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    tenant = await _get_tenant(db, cu["tenant_id"])
    if body.bot_token is not None:
        tenant.telegram_bot_token = body.bot_token or None
    if body.chat_id is not None:
        tenant.telegram_chat_id = body.chat_id or None
    await db.commit()
    return DataResponse(data={"bot_token": tenant.telegram_bot_token, "chat_id": tenant.telegram_chat_id})


@router.post("/test")
async def send_test(db: AsyncSession = Depends(get_db), cu: CurrentUser = Depends(_AUTH)):
    tenant = await _get_tenant(db, cu["tenant_id"])
    if not tenant.telegram_bot_token or not tenant.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    ok = await send_message(tenant.telegram_bot_token, tenant.telegram_chat_id, "✅ sphotel Telegram connected!")
    if not ok:
        raise HTTPException(status_code=502, detail="Telegram send failed — check bot token and chat ID")
    return DataResponse(data={"ok": True})


@router.post("/eod")
async def trigger_eod(
    for_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    cu: CurrentUser = Depends(_AUTH),
):
    tenant = await _get_tenant(db, cu["tenant_id"])
    ok = await send_eod_report(db, cu["tenant_id"], tenant.name, for_date)
    if not ok:
        raise HTTPException(status_code=502, detail="Telegram not configured or send failed")
    return DataResponse(data={"ok": True})
