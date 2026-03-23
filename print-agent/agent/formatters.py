"""Format dispatcher — selects receipt / KOT / EOD formatter by job_type.

All formatters are Python 3.6 compatible and read every bold/width/padding
setting from payload['print_template'], which the frontend caches locally
(localStorage) and sends with each offline print request.
"""
import sys
sys.path.insert(0, ".")
from agent.fmt_receipt import format_receipt
from agent.fmt_kot import format_kot
from agent.fmt_eod import format_eod


def format_job(payload):
    """Return rendered print_text string for any job type."""
    jt = payload.get("job_type", "receipt")
    if jt == "kot":
        return format_kot(payload)
    if jt == "eod":
        return format_eod(payload)
    return format_receipt(payload)
