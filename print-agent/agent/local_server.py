"""Local WebSocket server at 127.0.0.1 for offline print fallback.

PWA tries cloud first; falls back to ws://localhost:8765 when cloud unreachable.
Bound to loopback only — not accessible from other devices on the LAN.

Chrome Private Network Access preflight is handled via process_response.
"""
from __future__ import annotations

import asyncio
import json
import logging

try:
    import websockets
    from websockets.asyncio.server import ServerConnection as WebSocketServerProtocol
    from websockets.http11 import Request, Response
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

from agent.printer import print_receipt
from config.agent_config import agent_settings as cfg

log = logging.getLogger("print-agent.local")


def _add_pna_headers(
    connection: "WebSocketServerProtocol",
    request: "Request",
    response: "Response",
) -> "Response | None":
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return None


async def _handler(ws: "WebSocketServerProtocol") -> None:
    async for raw in ws:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            await ws.send(json.dumps({"ok": False, "error": "invalid json"}))
            continue
        try:
            print_receipt(payload)
            log.info("Local job printed: %s", payload.get("job_type", "?"))
            await ws.send(json.dumps({"ok": True}))
        except Exception as exc:
            log.error("Local print failed: %s", exc)
            await ws.send(json.dumps({"ok": False, "error": str(exc)}))


async def run_local_server() -> None:
    if not _AVAILABLE:
        log.warning("websockets not installed — local offline server disabled")
        return
    async with websockets.serve(
        _handler,
        "127.0.0.1",
        cfg.LOCAL_WS_PORT,
        process_response=_add_pna_headers,
    ):
        log.info("Local offline server listening on ws://127.0.0.1:%d", cfg.LOCAL_WS_PORT)
        await asyncio.Future()  # run forever
