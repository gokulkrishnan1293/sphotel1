import uuid

from sqlalchemy import UUID, Boolean, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin


class Section(Base, TenantMixin, TimestampMixin):
    """Floor / area grouping for tables (e.g. "Ground Floor", "Rooftop")."""

    __tablename__ = "sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(
        String(7), nullable=False, server_default=text("'#3b82f6'")
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    __table_args__ = (Index("idx_sections_tenant_id", "tenant_id"),)


class TableLayout(Base, TenantMixin, TimestampMixin):
    """A single table/seat in a section."""

    __tablename__ = "table_layouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("4")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    __table_args__ = (
        Index("idx_table_layouts_tenant_id", "tenant_id"),
        Index("idx_table_layouts_section_id", "section_id"),
    )
