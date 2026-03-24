"""WebSocket endpoint for Print Agent communication."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select, update

from app.db.session import async_session_maker
from app.models.print_agent import PrintAgent
from app.models.print_job import PrintJob
from app.websocket.print_agent_auth import authenticate_agent
from app.websocket.print_job_helpers import _reset_all_printing, _reset_stuck_jobs

router = APIRouter(tags=["websocket"])
log = logging.getLogger("sphotel.websocket")
# keepalive every N loops × 2 s ≈ 14 s — prevents Traefik idle-timeout disconnects
_KEEPALIVE_LOOPS = 7


@router.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket, api_key: str = Query(...)):
    await websocket.accept()
    agent = await authenticate_agent(api_key)
    if not agent:
        await websocket.close(code=1008, reason="Invalid API Key")
        return

    tenant_id, agent_id, printer_role = agent.tenant_id, agent.id, agent.printer_role
    await _reset_all_printing(tenant_id)
    disconnect_event = asyncio.Event()

    async def receive_acks() -> None:
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    if msg.get("type") == "print.job.confirmed" and (jid := msg.get("job_id")):
                        async with async_session_maker() as dba:
                            await dba.execute(
                                update(PrintJob)
                                .where(PrintJob.id == jid, PrintJob.tenant_id == tenant_id)
                                .values(status="done", updated_at=datetime.now(tz=timezone.utc))
                            )
                            await dba.commit()
                except Exception:
                    pass
        except Exception:
            # Any exception here (WebSocketDisconnect, network error, etc.) means
            # the receive channel is gone — signal the main loop to stop.
            disconnect_event.set()

    receiver_task = asyncio.create_task(receive_acks())
    try:
        loops = 0
        while not disconnect_event.is_set():
            if loops % 60 == 0:
                await _reset_stuck_jobs(tenant_id)
            msg = None
            async with async_session_maker() as db_poll:
                job = (await db_poll.execute(
                    select(PrintJob)
                    .where(PrintJob.status == "pending", PrintJob.tenant_id == tenant_id,
                           PrintJob.target_role == printer_role)
                    .order_by(PrintJob.created_at).limit(1)
                )).scalar_one_or_none()
                if job:
                    jid, payload, jtype = str(job.id), dict(job.payload), job.job_type
                    job.status, job.updated_at = "printing", datetime.now(tz=timezone.utc)
                    await db_poll.commit()
                    msg = {"type": "print.job", "job_id": jid,
                           "payload": {**payload, "job_id": jid, "job_type": jtype}}
            if msg:
                await websocket.send_text(json.dumps(msg))
            elif loops % _KEEPALIVE_LOOPS == 0:
                await websocket.send_text(json.dumps({"type": "keepalive"}))
            await asyncio.sleep(2)
            loops += 1
            if loops % 30 == 0:
                async with async_session_maker() as dbs:
                    await dbs.execute(update(PrintAgent).where(
                        PrintAgent.id == agent_id,
                    ).values(last_seen_at=datetime.now(tz=timezone.utc)))
                    await dbs.commit()
    except (WebSocketDisconnect, RuntimeError):
        log.info("Agent %s WS closed", agent_id)
    except Exception as e:
        log.error("Agent %s WS error: %s", agent_id, e)
    finally:
        receiver_task.cancel()
        await _reset_all_printing(tenant_id)
        async with async_session_maker() as db_close:
            await db_close.execute(
                update(PrintAgent).where(PrintAgent.id == agent_id).values(status="offline")
            )
            await db_close.commit()
