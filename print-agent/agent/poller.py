"""HTTP polling fallback — used when WebSocket is unavailable."""
import logging
import time

import requests

log = logging.getLogger("print-agent.poller")

import sys
sys.path.insert(0, ".")
from agent.updater import BASE, check_and_update
from config.agent_config import agent_settings as cfg


def _fetch_next_job(api_key):
    headers = {"X-Agent-Key": api_key, "Content-Type": "application/json"}
    params = {}
    if cfg.PRINTER_NAME:
        params["printer_name"] = cfg.PRINTER_NAME
    r = requests.get("{}/print-jobs/next".format(BASE), headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("data")


def _mark_done(api_key, job_id):
    headers = {"X-Agent-Key": api_key}
    requests.patch("{}/print-jobs/{}/status".format(BASE, job_id),
                   headers=headers, json={"status": "done"}, timeout=10).raise_for_status()


def _mark_failed(api_key, job_id, error):
    headers = {"X-Agent-Key": api_key}
    requests.patch("{}/print-jobs/{}/status".format(BASE, job_id),
                   headers=headers, json={"status": "failed", "error": error[:500]},
                   timeout=10).raise_for_status()


def run_http_poll(api_key):
    from agent.printer import print_receipt
    log.info("HTTP poll mode — polling every %ds", cfg.POLL_INTERVAL_SECONDS)
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
        if check_count % (3600 // cfg.POLL_INTERVAL_SECONDS) == 0:
            check_and_update()
