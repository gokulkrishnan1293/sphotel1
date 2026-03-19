"""Print Agent Authentication — one-time token activation → permanent API key."""
import json
import os
import sys
from pathlib import Path
from typing import Optional

import requests

_KEY_DIR = Path.home() / ".sphotel-agent"
_KEY_FILE = _KEY_DIR / ".agent_key"
_META_FILE = _KEY_DIR / "agent_meta.json"


def _ensure_dir():
    _KEY_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _KEY_DIR.chmod(0o700)
    except OSError:
        pass


def save_api_key(key, agent_id):
    _ensure_dir()
    _KEY_FILE.write_text(key, encoding="utf-8")
    _KEY_FILE.chmod(0o600)
    _META_FILE.write_text(json.dumps({"agent_id": agent_id}), encoding="utf-8")


def load_api_key():
    # type: () -> Optional[str]
    if not _KEY_FILE.exists():
        return None
    key = _KEY_FILE.read_text(encoding="utf-8").strip()
    return key or None


def load_agent_id():
    # type: () -> Optional[str]
    if not _META_FILE.exists():
        return None
    try:
        return json.loads(_META_FILE.read_text(encoding="utf-8")).get("agent_id")
    except (ValueError, OSError):
        return None


def activate(server_url, registration_token, agent_name):
    url = server_url.rstrip("/") + "/api/v1/print/agents/activate"
    try:
        resp = requests.post(
            url,
            json={"registration_token": registration_token, "name": agent_name},
            timeout=30,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print("[auth] Activation failed: {}".format(exc), file=sys.stderr)
        sys.exit(1)
    data = resp.json().get("data", {})
    api_key = data["agent_api_key"]
    agent_id = str(data["agent_id"])
    save_api_key(api_key, agent_id)
    print("[auth] Activated! Agent ID: {}".format(agent_id))
    print("[auth] API key saved to {}".format(_KEY_FILE))
    return api_key
