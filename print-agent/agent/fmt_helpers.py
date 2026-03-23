"""Shared formatting helpers. Python 3.6 compatible."""
from datetime import datetime, timedelta, timezone

_IST = timezone(timedelta(hours=5, minutes=30))
_B  = "\u00abB\u00bb"
_EB = "\u00ab/B\u00bb"


def bold(text, on):
    return "{}{}{}".format(_B, text, _EB) if on else text


def center(text, width):
    return text.center(width)


def divider(char="-", width=42):
    return char * width


def row(left, right, width):
    return left + " " * max(1, width - len(left) - len(right)) + right


def rs(paise):
    """Format paise as rupees string."""
    return "{:.2f}".format(paise / 100.0)


def inr(paise):
    """Format paise as INR with thousands separator."""
    return "{:,.2f}".format(paise / 100.0)


def ist(iso):
    """Parse ISO UTC timestamp and return IST string. strptime used (3.6 safe)."""
    try:
        dt = datetime.strptime(iso[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.astimezone(_IST).strftime("%d/%m/%y %H:%M")
    except Exception:
        return iso[:16]
