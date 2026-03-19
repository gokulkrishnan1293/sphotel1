import uuid

from sqlalchemy import UUID, Boolean, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin

FIXED_REPORT_TYPES = ["top_items", "waiter_performance", "payment_breakdown"]


class FixedReportConfig(Base, TenantMixin, TimestampMixin):
    __tablename__ = "fixed_report_configs"
    __table_args__ = (UniqueConstraint("tenant_id", "report_type"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    report_type: Mapped[str] = mapped_column(String, nullable=False)
    telegram_schedule: Mapped[str | None] = mapped_column(String, nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
