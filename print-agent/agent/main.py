"""Print Agent — main entrypoint. Python 3.6+ compatible.

Usage:
  python -m agent                          # run (WSS mode)
  python -m agent --register --token TOKEN --name "Counter Printer"
  python -m agent --poll                   # force HTTP polling mode
  python -m agent --update                 # check for update and exit
"""
import argparse
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("print-agent")

sys.path.insert(0, ".")
from agent.updater import check_and_update
from agent.poller import run_http_poll


def main():
    parser = argparse.ArgumentParser(description="sphotel Print Agent")
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--token")
    parser.add_argument("--name", default="Print Agent")
    parser.add_argument("--poll", action="store_true")
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()

    if args.register:
        if not args.token:
            print("Error: --token is required with --register", file=sys.stderr)
            sys.exit(1)
        from agent.auth import activate
        from config.agent_config import agent_settings as cfg
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

    check_and_update()

    from agent.local_http import start_local_http_server
    from config.agent_config import agent_settings as _cfg
    start_local_http_server(_cfg.LOCAL_HTTP_PORT)

    if args.poll:
        run_http_poll(api_key)
    else:
        try:
            from agent.ws_client import run_ws_client
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_ws_client())
        except ImportError:
            log.warning("websockets not installed — falling back to HTTP polling")
            run_http_poll(api_key)


if __name__ == "__main__":
    main()
