"""Route print jobs to the correct printer agent based on bill type and printer roles."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bill import Bill
from app.models.bill_enums import BillType
from app.models.print_agent import PrintAgent
from app.models.print_job import PrintJob
from app.services.print_payload import build_receipt_payload, build_kot_payload


async def _kot_target_role(db: AsyncSession, tenant_id: str) -> str:
    """Return 'kot' if a KOT printer agent is active (seen in last 5 min), else 'main'."""
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
    r = await db.execute(
        select(PrintAgent).where(
            PrintAgent.tenant_id == tenant_id,
            PrintAgent.printer_role == "kot",
            PrintAgent.last_seen_at > cutoff,
        )
    )
    return "kot" if r.scalar_one_or_none() else "main"


def _job(tenant_id: str, bill_id: uuid.UUID, job_type: str, payload: dict,
         target_role: str, printer_name: str | None = None) -> PrintJob:
    return PrintJob(tenant_id=tenant_id, bill_id=bill_id, job_type=job_type,
                    status="pending", payload=payload, target_role=target_role,
                    printer_name=printer_name)


async def create_print_job(
    db: AsyncSession,
    tenant_id: str,
    bill_id: uuid.UUID,
    job_type: str,
    printer_name: str | None,
) -> PrintJob:
    """Create print job(s).

    For parcel/online receipt triggers: also creates a KOT job routed to the
    KOT printer agent (fallback to main if no KOT agent is online).
    """
    if job_type == "kot":
        payload = await build_kot_payload(db, tenant_id, bill_id)
        job = _job(tenant_id, bill_id, "kot", payload, "kot", printer_name)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    # Fetch bill to decide if we also need a KOT job
    bill_r = await db.execute(select(Bill).where(Bill.id == bill_id, Bill.tenant_id == tenant_id))
    bill = bill_r.scalar_one_or_none()

    if bill and bill.bill_type in (BillType.PARCEL, BillType.ONLINE):
        kot_payload = await build_kot_payload(db, tenant_id, bill_id, include_pending=True)
        # Kitchen/merchant copy — dedicated KOT printer if online, else falls back to main
        kot_role = await _kot_target_role(db, tenant_id)
        db.add(_job(tenant_id, bill_id, "kot", kot_payload, kot_role))
        # Customer copy — always printed on main counter printer
        db.add(_job(tenant_id, bill_id, "kot", kot_payload, "main"))

    receipt_payload = await build_receipt_payload(db, tenant_id, bill_id)
    job = _job(tenant_id, bill_id, "receipt", receipt_payload, "main", printer_name)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def create_eod_print_job(db: AsyncSession, tenant_id: str, payload: dict) -> PrintJob:
    """Create an EOD print job. No bill_id needed."""
    job = _job(tenant_id, None, "eod_report", payload, "main", None)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job
