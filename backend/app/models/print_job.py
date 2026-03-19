import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    bill_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True)
    job_type: Mapped[str] = mapped_column(String, nullable=False)      # receipt | kot
    target_role: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'main'"))  # main | kot
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'pending'"))
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    printer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    __table_args__ = (
        Index("idx_print_jobs_tenant_status", "tenant_id", "status"),
    )
