import uuid

from sqlalchemy import UUID, Boolean, Index, Integer, String, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security.permissions import UserRole
from app.models.base import Base, TenantMixin, TimestampMixin


class TenantUser(Base, TenantMixin, TimestampMixin):
    __tablename__ = "tenant_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    # tenant_id inherited from TenantMixin (VARCHAR, NOT NULL, indexed)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        # create_type=False: PG ENUM is created by migration 0003, not by SA
        # values_callable: use enum .value (lowercase) to match DB labels
        SAEnum(UserRole, name="user_role", native_enum=True, create_type=False,
               values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    pin_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    totp_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    short_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    preferences: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )

    __table_args__ = (Index("idx_tenant_users_email", "email"),)
