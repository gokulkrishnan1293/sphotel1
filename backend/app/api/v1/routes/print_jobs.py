"""Print job endpoints — create (biller) + poll/update (print agent)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import bcrypt as _bcrypt
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, require_role
from app.core.security.permissions import UserRole
from app.db.session import get_db
from app.models.print_agent import PrintAgent
from app.models.print_job import PrintJob
from app.schemas.common import DataResponse
from app.schemas.print_job import CreatePrintJobRequest, PrintJobResponse, PrintJobStatusUpdate
from app.services.print_service import create_print_job

router = APIRouter(prefix="/print-jobs", tags=["print"])
_BILLING = require_role(UserRole.BILLER, UserRole.MANAGER, UserRole.ADMIN, UserRole.SUPER_ADMIN)


async def _verify_agent(
    x_agent_key: str = Header(default=""),
    db: AsyncSession = Depends(get_db),
) -> PrintAgent:
    """Verify X-Agent-Key against bcrypt hashes in print_agents; stamp last_seen_at."""
    if not x_agent_key:
        raise HTTPException(status_code=401, detail="Missing X-Agent-Key header")
    result = await db.execute(
        select(PrintAgent).where(PrintAgent.api_key_hash.is_not(None))
    )
    agents = result.scalars().all()
    matched: PrintAgent | None = None
    for agent in agents:
        if agent.api_key_hash and _bcrypt.checkpw(x_agent_key.encode(), agent.api_key_hash.encode()):
            matched = agent
            break
    if matched is None:
        raise HTTPException(status_code=401, detail="Invalid agent key")
    await db.execute(
        update(PrintAgent)
        .where(PrintAgent.id == matched.id)
        .values(last_seen_at=datetime.now(tz=timezone.utc), status="online")
    )
    await db.commit()
    return matched


@router.post("", response_model=DataResponse[PrintJobResponse], status_code=201)
async def create_job(
    body: CreatePrintJobRequest,
    cu: CurrentUser = Depends(_BILLING),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintJobResponse]:
    """Biller triggers a print job for a bill."""
    job = await create_print_job(db, cu["tenant_id"], body.bill_id, body.job_type, body.printer_name)
    return DataResponse(data=PrintJobResponse.model_validate(job))


@router.get("/next", response_model=DataResponse[PrintJobResponse | None])
async def next_job(
    printer_name: str | None = None,
    agent: PrintAgent = Depends(_verify_agent),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintJobResponse | None]:
    """Print agent polls for the next pending job (auto-filtered by tenant)."""
    q = (
        select(PrintJob)
        .where(
            PrintJob.status == "pending",
            PrintJob.tenant_id == agent.tenant_id,
            PrintJob.target_role == agent.printer_role,
        )
    )
    if printer_name:
        q = q.where(PrintJob.printer_name == printer_name)
    q = q.order_by(PrintJob.created_at).limit(1)
    job = (await db.execute(q)).scalar_one_or_none()
    if not job:
        return DataResponse(data=None)
    await db.execute(
        update(PrintJob)
        .where(PrintJob.id == job.id)
        .values(status="printing", updated_at=datetime.now(tz=timezone.utc))
    )
    await db.commit()
    await db.refresh(job)
    return DataResponse(data=PrintJobResponse.model_validate(job))


@router.patch("/{job_id}/status", response_model=DataResponse[PrintJobResponse])
async def update_status(
    job_id: uuid.UUID,
    body: PrintJobStatusUpdate,
    agent: PrintAgent = Depends(_verify_agent),
    db: AsyncSession = Depends(get_db),
) -> DataResponse[PrintJobResponse]:
    """Print agent marks a job as done or failed."""
    if body.status not in ("done", "failed"):
        raise HTTPException(400, "status must be 'done' or 'failed'")
    await db.execute(
        update(PrintJob)
        .where(PrintJob.id == job_id)
        .values(status=body.status, error=body.error, updated_at=datetime.now(tz=timezone.utc))
    )
    await db.commit()
    job = (await db.execute(select(PrintJob).where(PrintJob.id == job_id))).scalar_one()
    return DataResponse(data=PrintJobResponse.model_validate(job))
