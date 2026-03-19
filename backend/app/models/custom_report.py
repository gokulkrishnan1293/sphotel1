import uuid

from sqlalchemy import UUID, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantMixin, TimestampMixin


class CustomReport(Base, TenantMixin, TimestampMixin):
    __tablename__ = "custom_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    metric: Mapped[str] = mapped_column(String, nullable=False)
    # chart_type: bar | line | pie | table
    chart_type: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'bar'"))
    # telegram_schedule: null | daily | weekly
    telegram_schedule: Mapped[str | None] = mapped_column(String, nullable=True)
    dimension: Mapped[str | None] = mapped_column(String, nullable=True)
    days: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("7"))
