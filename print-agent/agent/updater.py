"""Auto-update — downloads new agent.exe from R2/S3 if server has a newer version."""
import hashlib
import logging
import os
import shutil
import sys

import requests

log = logging.getLogger("print-agent.updater")

sys.path.insert(0, ".")
from config.agent_config import agent_settings as cfg

BASE = cfg.SPHOTEL_API_URL.rstrip("/") + "/api/v1"
_EXE = sys.executable if getattr(sys, "frozen", False) else None


def check_and_update():
    """Download new exe if server has a newer version. Returns True if updated."""
    if not _EXE:
        log.info("[update] Not running as executable — skipping auto-update")
        return False
    try:
        r = requests.get("{}/print/agents/version".format(BASE), timeout=10)
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
                f.write(chunk)
                sha.update(chunk)
        if expected_sha and sha.hexdigest() != expected_sha:
            os.remove(tmp)
            log.error("[update] SHA256 mismatch — update aborted")
            return False
        shutil.move(_EXE, _EXE + ".bak")
        shutil.move(tmp, _EXE)
        os.chmod(_EXE, 0o755)
        log.info("[update] Updated — restarting")
        os.execv(_EXE, sys.argv)
    except Exception as exc:
        log.error("[update] Update failed: %s", exc)
    return False
