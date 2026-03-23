"""Local WebSocket server at 127.0.0.1 for offline print fallback.

PWA falls back to ws://localhost:8765 when cloud is unreachable.
Bound to loopback only — not accessible from other devices on the LAN.
Compatible with websockets 9.x (Python 3.6).
"""
import asyncio
import json
import logging
import functools

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
        # Auto-format if caller sent raw bill data instead of pre-rendered print_text
        if not payload.get("print_text"):
            try:
                from agent.formatters import format_job
                payload["print_text"] = format_job(payload)
            except Exception as exc:
                await ws.send(json.dumps({"ok": False, "error": "format error: {}".format(str(exc))}))
                continue
        try:
            from agent.printer import print_receipt
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, functools.partial(print_receipt, payload))
            log.info("Local WS job printed: %s", payload.get("job_type", "receipt"))
            await ws.send(json.dumps({"ok": True}))
        except Exception as exc:
            log.error("Local WS print failed: %s", exc)
            await ws.send(json.dumps({"ok": False, "error": str(exc)}))


async def run_local_server():
    if not _AVAILABLE:
        log.warning("websockets not installed — local WS server disabled")
        return
    try:
        async with websockets.serve(_handler, "127.0.0.1", cfg.LOCAL_WS_PORT):
            log.info("Local WS server on ws://127.0.0.1:%d", cfg.LOCAL_WS_PORT)
            while True:
                await asyncio.sleep(3600)
    except OSError as exc:
        log.error("Local WS server failed (port %d in use?): %s", cfg.LOCAL_WS_PORT, exc)
    except Exception as exc:
        log.error("Local WS server error: %s", exc)
