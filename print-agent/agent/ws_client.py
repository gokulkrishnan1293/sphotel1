"""WebSocket client — persistent WSS connection with local SQLite job queue."""
import asyncio
import json
import logging
import sys

import websockets

sys.path.insert(0, ".")
from agent.auth import load_api_key
from agent.job_queue import init_queue_db, enqueue, flush_queue
from config.agent_config import agent_settings as cfg

log = logging.getLogger("print-agent.ws")


async def _handle_job(ws, msg, conn):
    try:
        data = json.loads(msg)
    except ValueError:
        log.warning("Received non-JSON message: %s", msg[:80])
        return
    if data.get("type", "") != "print.job":
        return
    payload = data.get("payload", {})
    job_id = payload.get("job_id") or data.get("job_id", "unknown")
    log.info("Received job %s type=%s", job_id, payload.get("job_type", "receipt"))
    try:
        from agent.printer import print_receipt
        print_receipt(payload)
        await ws.send(json.dumps({"type": "print.job.confirmed", "job_id": job_id}))
        log.info("Job %s printed and confirmed", job_id)
    except Exception as exc:
        log.error("Job %s failed: %s — queuing locally", job_id, exc)
        enqueue(conn, str(job_id), payload)


async def _cloud_loop(conn):
    api_key = load_api_key()
    if not api_key:
        log.error("No API key. Run: python -m agent --register --token <TOKEN> --name <NAME>")
        sys.exit(1)
    base_url = cfg.SPHOTEL_API_URL.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = "{}/ws/agent?api_key={}".format(base_url.rstrip("/"), api_key)
    backoff = 1
    while True:
        try:
            log.info("Connecting to %s", ws_url.split("?")[0])
            async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as ws:
                log.info("Connected — flushing local queue")
                flush_queue(conn)
                backoff = 1
                async for message in ws:
                    await _handle_job(ws, str(message), conn)
        except websockets.exceptions.ConnectionClosed as exc:
            log.warning("WS closed: %s — retrying in %ds", exc, backoff)
        except OSError as exc:
            log.warning("Cannot reach server: %s — retrying in %ds", exc, backoff)
        except Exception as exc:
            log.error("Unexpected WS error: %s — retrying in %ds", exc, backoff)
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 30)


async def run_ws_client():
    conn = init_queue_db()
    from agent.local_server import run_local_server
    await asyncio.gather(_cloud_loop(conn), run_local_server())
