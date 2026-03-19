"""Unit tests for Story 1.2: DB migration framework & schema conventions.

These tests validate ORM model structure without requiring a live database.
"""

import sqlalchemy as sa

from app.models.audit_log import AuditLog
from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.tenant import Tenant
from app.models.user import TenantUser


def test_naming_convention_configured() -> None:
    """MetaData naming convention is set for deterministic constraint names."""
    convention = Base.metadata.naming_convention
    assert convention["ix"] == "idx_%(table_name)s_%(column_0_name)s"
    assert convention["pk"] == "pk_%(table_name)s"
    assert convention["uq"] == "uq_%(table_name)s_%(column_0_name)s"
    assert convention["fk"].startswith("fk_")


def test_tenant_table_name() -> None:
    assert Tenant.__tablename__ == "tenants"


def test_tenant_user_table_name() -> None:
    assert TenantUser.__tablename__ == "tenant_users"


def test_audit_log_table_name() -> None:
    assert AuditLog.__tablename__ == "audit_logs"


def test_tenant_columns() -> None:
    cols = {c.name: c for c in Tenant.__table__.columns}
    assert "id" in cols
    assert "name" in cols
    assert "slug" in cols
    assert "is_active" in cols
    assert "created_at" in cols
    assert "updated_at" in cols
    # No tenant_id on tenants itself
    assert "tenant_id" not in cols


def test_tenant_slug_unique() -> None:
    slug_col = Tenant.__table__.c["slug"]
    assert any(
        isinstance(c, sa.UniqueConstraint) and "slug" in [col.name for col in c.columns]
        for c in Tenant.__table__.constraints
    ) or slug_col.unique


def test_tenant_timestamps_are_timezone_aware() -> None:
    """Timestamps must use TIMESTAMPTZ (DateTime with timezone=True)."""
    for col_name in ("created_at", "updated_at"):
        col = Tenant.__table__.c[col_name]
        assert isinstance(col.type, sa.DateTime), f"{col_name} must be DateTime"
        assert col.type.timezone, f"{col_name} must have timezone=True (TIMESTAMPTZ)"


def test_tenant_user_has_tenant_id() -> None:
    """TenantUser uses TenantMixin — tenant_id must exist and be non-nullable."""
    assert issubclass(TenantUser, TenantMixin)
    col = TenantUser.__table__.c["tenant_id"]
    assert not col.nullable


def test_tenant_user_nullable_fields() -> None:
    """Credential fields are nullable; core fields are not."""
    cols = TenantUser.__table__.c
    assert cols["pin_hash"].nullable
    assert cols["email"].nullable
    assert cols["password_hash"].nullable
    assert cols["totp_secret"].nullable
    assert not cols["name"].nullable
    assert not cols["role"].nullable
    assert not cols["is_active"].nullable


def test_tenant_user_timestamps() -> None:
    assert issubclass(TenantUser, TimestampMixin)
    for col_name in ("created_at", "updated_at"):
        col = TenantUser.__table__.c[col_name]
        assert col.type.timezone, f"{col_name} must be TIMESTAMPTZ"


def test_audit_log_no_updated_at() -> None:
    """Audit log is append-only — no updated_at column."""
    col_names = {c.name for c in AuditLog.__table__.columns}
    assert "created_at" in col_names
    assert "updated_at" not in col_names


def test_audit_log_tenant_id_not_fk() -> None:
    """audit_logs.tenant_id is a plain VARCHAR — no FK constraint."""
    col = AuditLog.__table__.c["tenant_id"]
    assert not col.foreign_keys, "tenant_id on audit_logs must NOT be a FK"


def test_audit_log_indexes() -> None:
    index_names = {i.name for i in AuditLog.__table__.indexes}
    assert "idx_audit_logs_tenant_id" in index_names
    assert "idx_audit_logs_actor_id" in index_names


def test_no_float_money_columns() -> None:
    """No Float columns across any model — money must be INTEGER (paise)."""
    for model in (Tenant, TenantUser, AuditLog):
        for col in model.__table__.columns:
            assert not isinstance(col.type, sa.Float), (
                f"{model.__tablename__}.{col.name} uses Float — "
                "money must be INTEGER paise"
            )


def test_all_models_registered_in_metadata() -> None:
    table_names = set(Base.metadata.tables.keys())
    assert "tenants" in table_names
    assert "tenant_users" in table_names
    assert "audit_logs" in table_names
