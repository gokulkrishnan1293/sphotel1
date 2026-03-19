import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security.permissions import FoodType
from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.bill_enums import ItemStatus, sa_enum


class KotTicket(Base, TenantMixin, TimestampMixin):
    """Kitchen order ticket — snapshot of items fired to kitchen."""

    __tablename__ = "kot_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    bill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bills.id", ondelete="CASCADE"), nullable=False
    )
    ticket_number: Mapped[int] = mapped_column(Integer, nullable=False)
    fired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    ready_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ready_item_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_kot_tickets_tenant_id", "tenant_id"),
        Index("idx_kot_tickets_bill_id", "bill_id"),
    )


class BillItem(Base, TenantMixin, TimestampMixin):
    """Line item in a bill — price/name snapshot at order time."""

    __tablename__ = "bill_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    bill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bills.id", ondelete="CASCADE"), nullable=False
    )
    menu_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    food_type: Mapped[FoodType] = mapped_column(
        SAEnum(FoodType, name="food_type", native_enum=True, create_type=False,
               values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    status: Mapped[ItemStatus] = mapped_column(
        sa_enum(ItemStatus, "item_status"), nullable=False, server_default=text("'pending'")
    )
    kot_ticket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kot_tickets.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_price_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_bill_items_bill_id", "bill_id"),
        Index("idx_bill_items_tenant_id", "tenant_id"),
    )
