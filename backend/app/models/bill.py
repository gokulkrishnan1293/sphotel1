import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.bill_enums import BillStatus, BillType, PaymentMethod, sa_enum


class Bill(Base, TenantMixin, TimestampMixin):
    """A billing session — table dine-in, parcel, or online order."""

    __tablename__ = "bills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    bill_type: Mapped[BillType] = mapped_column(sa_enum(BillType, "bill_type"), nullable=False)
    status: Mapped[BillStatus] = mapped_column(
        sa_enum(BillStatus, "bill_status"), nullable=False, server_default=text("'draft'")
    )
    table_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("table_layouts.id", ondelete="SET NULL"), nullable=True
    )
    covers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reference_no: Mapped[str | None] = mapped_column(String, nullable=True)
    platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subtotal_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    discount_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    gst_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    total_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        sa_enum(PaymentMethod, "payment_method"), nullable=True
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bill_number: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant_users.id", ondelete="RESTRICT"), nullable=False
    )
    waiter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenant_users.id", ondelete="SET NULL"), nullable=True
    )

    __table_args__ = (
        Index("idx_bills_tenant_id", "tenant_id"),
        Index("idx_bills_tenant_status", "tenant_id", "status"),
        Index("idx_bills_table_id", "table_id"),
    )
