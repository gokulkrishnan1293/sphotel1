"""Local SQLite job queue for offline print fallback."""
import json
import logging
import sqlite3
import time
from pathlib import Path

log = logging.getLogger("print-agent.queue")

_DB_PATH = Path.home() / ".sphotel-agent" / "queue.db"


def init_queue_db():
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    conn.execute("""CREATE TABLE IF NOT EXISTS job_queue (
        id TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        attempts INTEGER NOT NULL DEFAULT 0,
        created_at REAL NOT NULL
    )""")
    conn.commit()
    return conn


def enqueue(conn, job_id, payload):
    conn.execute(
        "INSERT OR IGNORE INTO job_queue (id, payload, created_at) VALUES (?, ?, ?)",
        (job_id, json.dumps(payload), time.time()),
    )
    conn.commit()


def dequeue(conn):
    rows = conn.execute(
        "SELECT id, payload FROM job_queue ORDER BY created_at LIMIT 10"
    ).fetchall()
    return [(r[0], json.loads(r[1])) for r in rows]


def remove(conn, job_id):
    conn.execute("DELETE FROM job_queue WHERE id = ?", (job_id,))
    conn.commit()


def flush_queue(conn):
    """Print any jobs stored locally while offline."""
    from agent.printer import print_receipt
    for job_id, payload in dequeue(conn):
        try:
            print_receipt(payload)
            remove(conn, job_id)
            log.info("Flushed queued job %s", job_id)
        except Exception as exc:
            log.warning("Could not flush job %s: %s", job_id, exc)
