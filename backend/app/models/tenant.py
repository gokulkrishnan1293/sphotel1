import uuid
from typing import Any

from sqlalchemy import UUID, Boolean, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

from app.schemas.print_template import PrintTemplateConfig

_DEFAULT_PRINT_TEMPLATE: dict[str, Any] = PrintTemplateConfig().model_dump()


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    print_template: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    online_vendors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    telegram_bot_token: Mapped[str | None] = mapped_column(String, nullable=True)
    telegram_chat_id: Mapped[str | None] = mapped_column(String, nullable=True)
    keyboard_shortcuts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
