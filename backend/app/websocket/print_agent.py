"""WebSocket endpoints for Print Agent communication."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update

from app.db.session import async_session_maker
from app.models.print_agent import PrintAgent
from app.models.print_job import PrintJob

router = APIRouter(tags=["websocket"])
log = logging.getLogger("sphotel.websocket")

_PRINTING_TIMEOUT = timedelta(minutes=2)


async def _reset_stuck_jobs(tenant_id: str) -> None:
    """Reset printing→pending for jobs stuck > 2 min or on agent disconnect."""
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
    """On disconnect: reset all in-flight printing jobs back to pending."""
    async with async_session_maker() as db:
        await db.execute(
            update(PrintJob)
            .where(PrintJob.tenant_id == tenant_id, PrintJob.status == "printing")
            .values(status="pending", updated_at=datetime.now(tz=timezone.utc))
        )
        await db.commit()


@router.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket, api_key: str = Query(...)):
    """Persistent WebSocket connection for a print agent."""
    await websocket.accept()

    agent: PrintAgent | None = None
    async with async_session_maker() as db:
        result = await db.execute(select(PrintAgent).where(PrintAgent.api_key_hash.is_not(None)))
        for a in result.scalars().all():
            if a.api_key_hash and _bcrypt.checkpw(api_key.encode(), a.api_key_hash.encode()):
                agent = a
                break

        if not agent:
            await websocket.close(code=1008, reason="Invalid API Key")
            return

        agent.last_seen_at = datetime.now(tz=timezone.utc)
        agent.status = "online"
        await db.commit()

    tenant_id = agent.tenant_id
    agent_id = agent.id

    # Flush any jobs stuck in printing from a previous session
    await _reset_all_printing(tenant_id)

    async def receive_acks() -> None:
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "print.job.confirmed":
                        job_id = msg.get("job_id")
                        if job_id:
                            async with async_session_maker() as db_ack:
                                await db_ack.execute(
                                    update(PrintJob)
                                    .where(PrintJob.id == job_id, PrintJob.tenant_id == tenant_id)
                                    .values(status="done", updated_at=datetime.now(tz=timezone.utc))
                                )
                                await db_ack.commit()
                except ValueError:
                    pass
        except (WebSocketDisconnect, Exception):
            pass

    receiver_task = asyncio.create_task(receive_acks())

    try:
        loops = 0
        while True:
            # Safety net: reset jobs stuck in printing > 2 min
            if loops % 60 == 0:
                await _reset_stuck_jobs(tenant_id)

            async with async_session_maker() as db_poll:
                job = (await db_poll.execute(
                    select(PrintJob)
                    .where(PrintJob.status == "pending", PrintJob.tenant_id == tenant_id)
                    .order_by(PrintJob.created_at)
                    .limit(1)
                )).scalar_one_or_none()

                if job:
                    job.status = "printing"
                    job.updated_at = datetime.now(tz=timezone.utc)
                    await db_poll.commit()
                    job_data = {**dict(job.payload), "job_id": str(job.id), "job_type": job.job_type}
                    await websocket.send_text(json.dumps({"type": "print.job", "job_id": str(job.id), "payload": job_data}))

            await asyncio.sleep(2)
            loops += 1
            if loops % 30 == 0:
                async with async_session_maker() as db_stamp:
                    await db_stamp.execute(update(PrintAgent).where(PrintAgent.id == agent_id).values(last_seen_at=datetime.now(tz=timezone.utc)))
                    await db_stamp.commit()

    except WebSocketDisconnect:
        log.info("Agent %s disconnected", agent_id)
    except Exception as e:
        log.error("Agent WS error: %s", e)
    finally:
        receiver_task.cancel()
        await _reset_all_printing(tenant_id)
        async with async_session_maker() as db_close:
            await db_close.execute(update(PrintAgent).where(PrintAgent.id == agent_id).values(status="offline"))
            await db_close.commit()
