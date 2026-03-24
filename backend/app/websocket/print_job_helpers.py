"""Shared helpers for print job lifecycle — stuck-job reset and in-flight rollback."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from app.db.session import async_session_maker
from app.models.print_job import PrintJob

_PRINTING_TIMEOUT = timedelta(minutes=2)


async def _reset_stuck_jobs(tenant_id: str) -> None:
    """Reset printing→pending for jobs stuck longer than _PRINTING_TIMEOUT."""
    cutoff = datetime.now(tz=timezone.utc) - _PRINTING_TIMEOUT
    async with async_session_maker() as db:
        await db.execute(
            update(PrintJob)
            .where(
                PrintJob.tenant_id == tenant_id,
                PrintJob.status == "printing",
                PrintJob.updated_at < cutoff,
            )
            .values(status="pending", updated_at=datetime.now(tz=timezone.utc))
        )
        await db.commit()


async def _reset_all_printing(tenant_id: str) -> None:
    """On agent disconnect: reset all in-flight printing jobs back to pending."""
    async with async_session_maker() as db:
        await db.execute(
            update(PrintJob)
            .where(PrintJob.tenant_id == tenant_id, PrintJob.status == "printing")
            .values(status="pending", updated_at=datetime.now(tz=timezone.utc))
        )
        await db.commit()
