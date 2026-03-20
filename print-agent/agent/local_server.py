"""Local WebSocket server at 127.0.0.1 for offline print fallback.

PWA falls back to ws://localhost:8765 when cloud is unreachable.
Bound to loopback only — not accessible from other devices on the LAN.
Compatible with websockets 9.x (Python 3.6).
"""
import asyncio
import json
import logging

try:
    import websockets
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

import sys
sys.path.insert(0, ".")
from config.agent_config import agent_settings as cfg

log = logging.getLogger("print-agent.local")


async def _handler(ws, path):
    async for raw in ws:
        try:
            payload = json.loads(raw)
        except ValueError:
            await ws.send(json.dumps({"ok": False, "error": "invalid json"}))
            continue
        try:
            from agent.printer import print_receipt
            print_receipt(payload)
            log.info("Local job printed: %s", payload.get("job_type", "?"))
            await ws.send(json.dumps({"ok": True}))
        except Exception as exc:
            log.error("Local print failed: %s", exc)
            await ws.send(json.dumps({"ok": False, "error": str(exc)}))


async def run_local_server():
    if not _AVAILABLE:
        log.warning("websockets not installed — local server disabled")
        return
    async with websockets.serve(_handler, "127.0.0.1", cfg.LOCAL_WS_PORT):
        log.info("Local server on ws://127.0.0.1:%d", cfg.LOCAL_WS_PORT)
        while True:
            await asyncio.sleep(3600)
