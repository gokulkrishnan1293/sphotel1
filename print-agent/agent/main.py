"""Print Agent — main entrypoint. Supports WSS (primary) with HTTP poll fallback.

Usage:
  python -m agent                          # run normally (WSS mode)
  python -m agent --register --token TOKEN --name "Counter Printer"  # first-time setup
  python -m agent --poll                   # force HTTP polling mode (legacy)
  python -m agent --update                 # check for updates and restart if newer
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import logging
import os
import shutil
import sys
import time

import requests

sys.path.insert(0, ".")
from config.agent_config import agent_settings as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("print-agent")

BASE = cfg.SPHOTEL_API_URL.rstrip("/") + "/api/v1"
_EXE = sys.executable if getattr(sys, "frozen", False) else None  # set when built with PyInstaller


# ── Auto-update ───────────────────────────────────────────────────────────────

def check_and_update() -> bool:
    """Download new exe if server has a newer version. Returns True if updated."""
    if not _EXE:
        log.info("[update] Not running as executable — skipping auto-update")
        return False
    try:
        r = requests.get(f"{BASE}/print/agents/version", timeout=10)
        r.raise_for_status()
        info = r.json().get("data", {})
        download_url = info.get("download_url")
        expected_sha = info.get("sha256")
        if not download_url:
            log.info("[update] No download URL configured on server")
            return False
        log.info("[update] Downloading new version from %s", download_url)
        dl = requests.get(download_url, timeout=120, stream=True)
        dl.raise_for_status()
        tmp = _EXE + ".new"
        sha = hashlib.sha256()
        with open(tmp, "wb") as f:
            for chunk in dl.iter_content(65536):
                f.write(chunk); sha.update(chunk)
        if expected_sha and sha.hexdigest() != expected_sha:
            os.remove(tmp)
            log.error("[update] SHA256 mismatch — update aborted")
            return False
        backup = _EXE + ".bak"
        shutil.move(_EXE, backup)
        shutil.move(tmp, _EXE)
        os.chmod(_EXE, 0o755)
        log.info("[update] Updated successfully — restarting")
        os.execv(_EXE, sys.argv)   # replace current process
    except Exception as exc:
        log.error("[update] Update failed: %s", exc)
    return False


# ── HTTP polling fallback ─────────────────────────────────────────────────────

def _fetch_next_job(api_key: str) -> dict | None:
    headers = {"X-Agent-Key": api_key, "Content-Type": "application/json"}
    params = {}
    if cfg.PRINTER_NAME:
        params["printer_name"] = cfg.PRINTER_NAME
    r = requests.get(f"{BASE}/print-jobs/next", headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("data")


def _mark_done(api_key: str, job_id: str) -> None:
    headers = {"X-Agent-Key": api_key}
    requests.patch(f"{BASE}/print-jobs/{job_id}/status", headers=headers,
                   json={"status": "done"}, timeout=10).raise_for_status()


def _mark_failed(api_key: str, job_id: str, error: str) -> None:
    headers = {"X-Agent-Key": api_key}
    requests.patch(f"{BASE}/print-jobs/{job_id}/status", headers=headers,
                   json={"status": "failed", "error": error[:500]}, timeout=10).raise_for_status()


def run_http_poll(api_key: str) -> None:
    from agent.printer import print_receipt
    log.info("HTTP poll mode — polling %s every %ds", BASE, cfg.POLL_INTERVAL_SECONDS)
    check_count = 0
    while True:
        try:
            job = _fetch_next_job(api_key)
            if job:
                job_id = job["id"]
                try:
                    print_receipt(job["payload"])
                    _mark_done(api_key, job_id)
                    log.info("Job %s done", job_id)
                except Exception as exc:
                    log.error("Job %s failed: %s", job_id, exc)
                    try:
                        _mark_failed(api_key, job_id, str(exc))
                    except Exception:
                        pass
        except requests.exceptions.ConnectionError:
            log.warning("Cannot reach backend, retrying...")
        except Exception as exc:
            log.error("Unexpected error: %s", exc)
        time.sleep(cfg.POLL_INTERVAL_SECONDS)
        check_count += 1
        if check_count % (3600 // cfg.POLL_INTERVAL_SECONDS) == 0:  # every ~1 hour
            check_and_update()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="sphotel Print Agent")
    parser.add_argument("--register", action="store_true", help="Activate agent with one-time token")
    parser.add_argument("--token", help="Registration token from Admin UI")
    parser.add_argument("--name", default="Print Agent", help="Agent display name")
    parser.add_argument("--poll", action="store_true", help="Force HTTP polling mode")
    parser.add_argument("--update", action="store_true", help="Check for update and exit")
    args = parser.parse_args()

    if args.register:
        if not args.token:
            print("Error: --token is required with --register", file=sys.stderr)
            sys.exit(1)
        from agent.auth import activate
        activate(cfg.SPHOTEL_API_URL, args.token, args.name)
        return

    if args.update:
        check_and_update()
        return

    from agent.auth import load_api_key
    api_key = load_api_key()
    if not api_key:
        log.error("Not activated. Run: python -m agent --register --token <TOKEN> --name <NAME>")
        sys.exit(1)

    check_and_update()  # check on every startup

    if args.poll:
        run_http_poll(api_key)
    else:
        try:
            from agent.ws_client import run_ws_client
            asyncio.run(run_ws_client())
        except ImportError:
            log.warning("websockets not installed — falling back to HTTP polling")
            run_http_poll(api_key)


if __name__ == "__main__":
    main()
