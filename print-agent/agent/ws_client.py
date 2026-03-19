"""WebSocket client — persistent WSS connection to cloud with local SQLite job queue."""
from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path

import websockets

sys.path.insert(0, ".")
from agent.auth import load_api_key
from agent.printer import print_receipt
from config.agent_config import agent_settings as cfg

log = logging.getLogger("print-agent.ws")

_DB_PATH = Path.home() / ".sphotel-agent" / "queue.db"


def _init_queue_db() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS job_queue (
            id TEXT PRIMARY KEY,
            payload TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            created_at REAL NOT NULL
        )"""
    )
    conn.commit()
    return conn


def _enqueue(conn: sqlite3.Connection, job_id: str, payload: dict) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO job_queue (id, payload, created_at) VALUES (?, ?, ?)",
        (job_id, json.dumps(payload), time.time()),
    )
    conn.commit()


def _dequeue(conn: sqlite3.Connection) -> list[tuple[str, dict]]:
    rows = conn.execute(
        "SELECT id, payload FROM job_queue ORDER BY created_at LIMIT 10"
    ).fetchall()
    return [(r[0], json.loads(r[1])) for r in rows]


def _remove(conn: sqlite3.Connection, job_id: str) -> None:
    conn.execute("DELETE FROM job_queue WHERE id = ?", (job_id,))
    conn.commit()


def _flush_local_queue(conn: sqlite3.Connection) -> None:
    """Attempt to print any jobs stored locally while offline."""
    pending = _dequeue(conn)
    for job_id, payload in pending:
        try:
            print_receipt(payload)
            _remove(conn, job_id)
            log.info("Flushed queued job %s", job_id)
        except Exception as exc:
            log.warning("Could not flush job %s: %s", job_id, exc)


async def _handle_job(ws: websockets.ClientConnection, msg: str, conn: sqlite3.Connection) -> None:
    try:
        data = json.loads(msg)
    except json.JSONDecodeError:
        log.warning("Received non-JSON message: %s", msg[:80])
        return

    msg_type = data.get("type", "")
    if msg_type != "print.job":
        return

    payload = data.get("payload", {})
    job_id = payload.get("job_id") or data.get("job_id", "unknown")
    log.info("Received print job %s type=%s", job_id, payload.get("job_type", "receipt"))

    try:
        print_receipt(payload)
        ack = json.dumps({"type": "print.job.confirmed", "job_id": job_id})
        await ws.send(ack)
        log.info("Job %s printed and confirmed", job_id)
    except Exception as exc:
        log.error("Job %s failed: %s — queuing locally", job_id, exc)
        _enqueue(conn, str(job_id), payload)


async def _cloud_loop(conn: sqlite3.Connection) -> None:
    """Persistent cloud WS connection with exponential backoff."""
    api_key = load_api_key()
    if not api_key:
        log.error("No API key found. Run: python -m agent --register --token <TOKEN> --name <NAME>")
        sys.exit(1)
    base_url = cfg.SPHOTEL_API_URL.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = f"{base_url}/ws/agent?api_key={api_key}"
    backoff = 1
    while True:
        try:
            log.info("Connecting to %s", ws_url.split("?")[0])
            async with websockets.connect(ws_url, ping_interval=30, ping_timeout=10) as ws:
                log.info("Connected — flushing local queue")
                _flush_local_queue(conn)
                backoff = 1
                async for message in ws:
                    await _handle_job(ws, str(message), conn)
        except websockets.exceptions.ConnectionClosed as exc:
            log.warning("WS connection closed: %s — retrying in %ds", exc, backoff)
        except OSError as exc:
            log.warning("Cannot reach server: %s — retrying in %ds", exc, backoff)
        except Exception as exc:
            log.error("Unexpected WS error: %s — retrying in %ds", exc, backoff)
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 30)


async def run_ws_client() -> None:
    """Run cloud WS + local offline server concurrently."""
    conn = _init_queue_db()
    from agent.local_server import run_local_server
    await asyncio.gather(
        _cloud_loop(conn),
        run_local_server(),
    )
