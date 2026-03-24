"""API-key authentication for print agents."""
from __future__ import annotations

from datetime import datetime, timezone

import bcrypt as _bcrypt
from sqlalchemy import select

from app.db.session import async_session_maker
from app.models.print_agent import PrintAgent


async def authenticate_agent(api_key: str) -> PrintAgent | None:
    """Return the matched PrintAgent and mark it online, or None if auth fails."""
    async with async_session_maker() as db:
        result = await db.execute(
            select(PrintAgent).where(PrintAgent.api_key_hash.is_not(None))
        )
        matched: PrintAgent | None = None
        for a in result.scalars().all():
            if a.api_key_hash and _bcrypt.checkpw(api_key.encode(), a.api_key_hash.encode()):
                matched = a
                break
        if not matched:
            return None
        matched.last_seen_at = datetime.now(tz=timezone.utc)
        matched.status = "online"
        await db.commit()
        return matched
