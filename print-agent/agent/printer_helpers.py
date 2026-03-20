"""Shared ESC/POS formatting utilities for the print agent."""
from datetime import datetime, timedelta, timezone

from config.agent_config import agent_settings as cfg

_IST = timezone(timedelta(hours=5, minutes=30))


def _to_ist(iso: str) -> str:
    """Parse UTC ISO timestamp, return formatted in IST."""
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(_IST).strftime("%d/%m/%y %H:%M")
    except ValueError:
        return iso


def _center(text: str, width: int) -> str:
    return text.center(width)


def _divider(char: str = "-", width: int = 42) -> str:
    return char * width


def _dots(width: int = 42) -> str:
    return "." * width


def _row_left_right(left: str, right: str, width: int) -> str:
    gap = width - len(left) - len(right)
    return left + " " * max(1, gap) + right


def _format_rupees(paise: int) -> str:
    return f"{paise / 100:.2f}"


def _now_str() -> str:
    return datetime.now(_IST).strftime("%d/%m/%y %H:%M")
