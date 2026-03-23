"""Local HTTP server on 127.0.0.1 — offline print fallback. Python 3.6 compatible.

Browser POSTs bill data to http://127.0.0.1:8766/print when cloud is unreachable.
Runs in a daemon thread alongside the main async loop.
"""
import json
import logging
import threading

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    _OK = True
except ImportError:
    _OK = False

import sys
sys.path.insert(0, ".")

log = logging.getLogger("print-agent.local-http")


class _Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._reply(200, {})

    def do_GET(self):
        if self.path == "/health":
            self._reply(200, {"ok": True})
        else:
            self._reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/print":
            self._reply(404, {"error": "not found"})
            return
        n = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
        except ValueError:
            self._reply(400, {"ok": False, "error": "invalid json"})
            return
        if not payload.get("print_text"):
            try:
                from agent.formatters import format_job
                payload["print_text"] = format_job(payload)
            except Exception as exc:
                self._reply(400, {"ok": False, "error": "format error: {}".format(exc)})
                return
        try:
            from agent.printer import print_receipt
            print_receipt(payload)
            log.info("Local HTTP job printed ok")
            self._reply(200, {"ok": True})
        except Exception as exc:
            log.error("Local HTTP print error: %s", exc)
            self._reply(500, {"ok": False, "error": str(exc)})

    def _reply(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # suppress default access log


def start_local_http_server(port):
    if not _OK:
        log.warning("http.server unavailable — local HTTP disabled")
        return
    try:
        server = HTTPServer(("127.0.0.1", port), _Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        log.info("Local HTTP server on http://127.0.0.1:%d/print", port)
    except Exception as exc:
        log.error("Local HTTP server failed to start (port %d): %s", port, exc)
