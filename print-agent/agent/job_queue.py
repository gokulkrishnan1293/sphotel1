"""Local SQLite job queue for offline print fallback."""
import json
import logging
import sqlite3
import time
from pathlib import Path

log = logging.getLogger("print-agent.queue")

_DB_PATH = Path.home() / ".sphotel-agent" / "queue.db"


def _connect():
    """Open a connection safe for use in any thread."""
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(_DB_PATH), check_same_thread=False)


def init_queue_db():
    conn = _connect()
    conn.execute("""CREATE TABLE IF NOT EXISTS job_queue (
        id TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        created_at REAL NOT NULL
    )""")
    conn.commit()
    conn.close()


def enqueue(job_id, payload):
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO job_queue (id, payload, created_at) VALUES (?, ?, ?)",
            (job_id, json.dumps(payload), time.time()),
        )
        conn.commit()
    finally:
        conn.close()


def flush_queue():
    """Print any jobs stored locally while offline."""
    from agent.printer import print_receipt
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, payload FROM job_queue ORDER BY created_at LIMIT 10"
        ).fetchall()
        jobs = [(r[0], json.loads(r[1])) for r in rows]
    finally:
        conn.close()
    for job_id, payload in jobs:
        try:
            print_receipt(payload)
            conn2 = _connect()
            try:
                conn2.execute("DELETE FROM job_queue WHERE id = ?", (job_id,))
                conn2.commit()
            finally:
                conn2.close()
            log.info("Flushed queued job %s", job_id)
        except Exception as exc:
            log.warning("Could not flush job %s: %s", job_id, exc)
