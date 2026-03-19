"""Print agent management endpoints — registration, activation, list, revoke, version."""
from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.print_agent import PrintAgent
from app.schemas.common import DataResponse

router = APIRouter(prefix="/print/agents", tags=["print-agents"])
_ADMIN = require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN)


def _hash(value: str) -> str:
    return _bcrypt.hashpw(value.encode(), _bcrypt.gensalt()).decode()


def _verify(value: str, hashed: str) -> bool:
    return _bcrypt.checkpw(value.encode(), hashed.encode())


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegisterTokenResponse(BaseModel):
    token: str
    expires_in_seconds: int = 86400


class ActivateRequest(BaseModel):
    registration_token: str
    name: str


class ActivateResponse(BaseModel):
    agent_id: uuid.UUID
    agent_api_key: str


class PrintAgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    printer_role: str
    last_seen_at: datetime | None
    printer_config: dict | None
    model_config = {"from_attributes": True}


class SetRoleRequest(BaseModel):
    printer_role: str  # main | kot


class VersionResponse(BaseModel):
    version: str
    download_url: str | None = None
    sha256: str | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _verify_agent_key(x_agent_key: str = Header(default="")) -> str:
    """Return agent key; caller must verify against DB hash."""
    if not x_agent_key:
        raise HTTPException(status_code=401, detail="Missing X-Agent-Key header")
    return x_agent_key


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/register-token",
    response_model=DataResponse[RegisterTokenResponse],
    status_code=201,
)
async def register_token(
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[RegisterTokenResponse]:
    """Admin generates a 24-hour one-time registration token."""
    token = secrets.token_urlsafe(32)
    expires = datetime.now(tz=timezone.utc) + timedelta(hours=24)
    agent = PrintAgent(
        tenant_id=cu["tenant_id"],
        name="pending",
        registration_token_hash=_hash(token),
        registration_token_expires_at=expires,
    )
    db.add(agent)
    await db.commit()
    return DataResponse(data=RegisterTokenResponse(token=token))


@router.post("/activate", response_model=DataResponse[ActivateResponse])
async def activate(
    body: ActivateRequest,
    db: AsyncSession = Depends(get_db),
) -> DataResponse[ActivateResponse]:
    """Print agent exchanges one-time token for a permanent API key."""
    result = await db.execute(
        select(PrintAgent).where(
            PrintAgent.name == "pending",
            PrintAgent.registration_token_hash.is_not(None),
        )
    )
    agents = result.scalars().all()
    now = datetime.now(tz=timezone.utc)

    matched: PrintAgent | None = None
    for agent in agents:
        if agent.registration_token_expires_at and agent.registration_token_expires_at < now:
            continue
        if agent.registration_token_hash and _verify(body.registration_token, agent.registration_token_hash):
            matched = agent
            break

    if matched is None:
        raise HTTPException(status_code=410, detail="Token invalid, expired, or already used")

    api_key = secrets.token_urlsafe(40)
    matched.api_key_hash = _hash(api_key)
    matched.name = body.name
    matched.registration_token_hash = None          # single-use: clear after activation
    matched.registration_token_expires_at = None
    matched.status = "online"
    matched.last_seen_at = now
    await db.commit()

    return DataResponse(data=ActivateResponse(agent_id=matched.id, agent_api_key=api_key))


@router.get("", response_model=DataResponse[list[PrintAgentResponse]])
async def list_agents(
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[list[PrintAgentResponse]]:
    """List all registered print agents for the tenant."""
    result = await db.execute(
        select(PrintAgent)
        .where(PrintAgent.tenant_id == cu["tenant_id"])
        .order_by(PrintAgent.created_at)
    )
    agents = result.scalars().all()
    return DataResponse(data=[PrintAgentResponse.model_validate(a) for a in agents])


@router.patch("/{agent_id}/role", response_model=DataResponse[PrintAgentResponse])
async def set_agent_role(
    agent_id: uuid.UUID,
    body: SetRoleRequest,
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintAgentResponse]:
    """Set printer role (main | kot) for an agent."""
    if body.printer_role not in ("main", "kot"):
        raise HTTPException(400, "printer_role must be 'main' or 'kot'")
    await db.execute(
        sa_update(PrintAgent)
        .where(PrintAgent.id == agent_id, PrintAgent.tenant_id == cu["tenant_id"])
        .values(printer_role=body.printer_role)
    )
    await db.commit()
    result = await db.execute(select(PrintAgent).where(PrintAgent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(404, "Agent not found")
    return DataResponse(data=PrintAgentResponse.model_validate(agent))


@router.delete("/{agent_id}", status_code=204)
async def revoke_agent(
    agent_id: uuid.UUID,
    cu: CurrentUser = Depends(_ADMIN),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Admin revokes a print agent's API key."""
    result = await db.execute(
        select(PrintAgent).where(
            PrintAgent.id == agent_id,
            PrintAgent.tenant_id == cu["tenant_id"],
        )
    )
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()


@router.get("/version", response_model=DataResponse[VersionResponse])
async def get_version() -> DataResponse[VersionResponse]:
    """Print agent polls this on startup and daily to check for updates."""
    return DataResponse(
        data=VersionResponse(
            version=settings.VERSION,
            download_url=getattr(settings, "AGENT_DOWNLOAD_URL", None),
            sha256=getattr(settings, "AGENT_SHA256", None),
        )
    )
