"""Print Agent Launcher — Windows Service entrypoint with auto-update via S3/R2."""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, ".")
from config.agent_config import agent_settings as cfg

log = logging.getLogger("print-agent.launcher")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_AGENT_DIR = Path.home() / ".sphotel-agent"
_AGENT_EXE = _AGENT_DIR / "agent.exe"
_VERSION_FILE = _AGENT_DIR / "VERSION"
_UPDATE_CHECK_HOUR = 3  # daily check at 03:xx local time

VERSION_ENDPOINT = cfg.SPHOTEL_API_URL.rstrip("/") + "/api/v1/print/agents/version"


def _current_version() -> str:
    if _VERSION_FILE.exists():
        return _VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_for_update() -> bool:
    """Check version endpoint; download, verify, and replace agent.exe if newer."""
    try:
        resp = requests.get(VERSION_ENDPOINT, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", {})
    except Exception as exc:
        log.warning("Version check failed: %s", exc)
        return False

    remote_version: str = data.get("version", "")
    download_url: str | None = data.get("download_url")
    expected_sha256: str | None = data.get("sha256")

    if not remote_version or remote_version == _current_version():
        log.info("Agent is up to date (%s)", remote_version)
        return False

    if not download_url:
        log.info("Newer version %s available but no download URL yet", remote_version)
        return False

    log.info("Downloading agent %s from %s", remote_version, download_url)
    tmp = _AGENT_DIR / "agent.exe.tmp"
    try:
        with requests.get(download_url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(65536):
                    f.write(chunk)
    except Exception as exc:
        log.error("Download failed: %s", exc)
        tmp.unlink(missing_ok=True)
        return False

    if expected_sha256 and _sha256_file(tmp) != expected_sha256:
        log.error("SHA256 mismatch — aborting update")
        tmp.unlink(missing_ok=True)
        return False

    shutil.move(str(tmp), str(_AGENT_EXE))
    _VERSION_FILE.write_text(remote_version, encoding="utf-8")
    log.info("Updated to %s — will restart agent subprocess", remote_version)
    return True


def _start_agent_process() -> subprocess.Popen:
    """Start the agent subprocess (WS client or HTTP polling fallback)."""
    if _AGENT_EXE.exists():
        cmd = [str(_AGENT_EXE)]
    else:
        cmd = [sys.executable, "-m", "agent"]
    log.info("Starting agent: %s", " ".join(cmd))
    return subprocess.Popen(cmd, cwd=str(_AGENT_DIR.parent))


def run() -> None:
    """Main launcher loop — manages agent subprocess and daily update checks."""
    log.info("Launcher started (agent dir: %s)", _AGENT_DIR)
    _AGENT_DIR.mkdir(parents=True, exist_ok=True)

    check_for_update()
    proc = _start_agent_process()

    last_update_check_day: int = -1

    while True:
        time.sleep(60)

        # Restart if subprocess died
        if proc.poll() is not None:
            log.warning("Agent process exited (code %s) — restarting", proc.returncode)
            proc = _start_agent_process()

        # Daily update check at 03:xx
        now = datetime.now(tz=timezone.utc)
        if now.hour == _UPDATE_CHECK_HOUR and now.day != last_update_check_day:
            last_update_check_day = now.day
            updated = check_for_update()
            if updated:
                log.info("Restarting agent subprocess after update")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                proc = _start_agent_process()


if __name__ == "__main__":
    run()
