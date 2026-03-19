import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TenantFeatureFlags(Base):
    """Per-tenant feature flag settings. One row per tenant; tenant_id is PK."""

    __tablename__ = "tenant_feature_flags"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    waiter_mode: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    suggestion_engine: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    telegram_alerts: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    gst_module: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    payroll_rewards: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    discount_complimentary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    waiter_transfer: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    bill_close_ux: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
