import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security.permissions import FoodType
from app.models.base import Base, TenantMixin, TimestampMixin


class MenuItemVariant(Base, TenantMixin):
    __tablename__ = "menu_item_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    menu_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    parcel_price_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    vendor_prices: Mapped[list["MenuItemVendorPrice"]] = relationship("MenuItemVendorPrice", foreign_keys="MenuItemVendorPrice.variant_id", cascade="all, delete-orphan", lazy="selectin")


class MenuItemVendorPrice(Base, TenantMixin):
    __tablename__ = "menu_item_vendor_prices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    menu_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=True)
    variant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("menu_item_variants.id", ondelete="CASCADE"), nullable=True)
    vendor_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("menu_item_id", "vendor_slug", name="uq_vendor_price_item"),
        UniqueConstraint("variant_id", "vendor_slug", name="uq_vendor_price_variant"),
    )


class MenuItem(Base, TenantMixin, TimestampMixin):
    __tablename__ = "menu_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    food_type: Mapped[FoodType] = mapped_column(
        SAEnum(FoodType, name="food_type", native_enum=True, create_type=False, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False, server_default=text("'veg'"),
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    parcel_price_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)

    variants: Mapped[list[MenuItemVariant]] = relationship("MenuItemVariant", foreign_keys="MenuItemVariant.menu_item_id", cascade="all, delete-orphan", order_by="MenuItemVariant.display_order", lazy="selectin")
    vendor_prices: Mapped[list[MenuItemVendorPrice]] = relationship("MenuItemVendorPrice", foreign_keys="MenuItemVendorPrice.menu_item_id", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_menu_items_tenant_id", "tenant_id"),
        Index("idx_menu_items_tenant_category", "tenant_id", "category"),
        UniqueConstraint("tenant_id", "short_code", name="uq_menu_items_tenant_short_code", deferrable=True, initially="DEFERRED"),
    )
