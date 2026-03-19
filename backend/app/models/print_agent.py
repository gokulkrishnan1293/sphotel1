"""PrintAgent model — per-agent authentication and status tracking."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PrintAgent(Base):
    __tablename__ = "print_agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # one-time registration token (bcrypt hash); cleared after activation
    registration_token_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    registration_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # permanent api key hash (bcrypt); present after activation
    api_key_hash: Mapped[str | None] = mapped_column(String, nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'offline'"))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # main | kot
    printer_role: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'main'"))

    # {"printer_type": "usb|network|file", "host": "...", "port": 9100}
    printer_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    __table_args__ = (Index("idx_print_agents_tenant", "tenant_id"),)
