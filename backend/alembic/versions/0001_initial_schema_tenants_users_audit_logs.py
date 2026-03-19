"""initial schema: tenants, tenant_users, audit_logs

Revision ID: 0001
Revises:
Create Date: 2026-03-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tenants ────────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenants")),
        sa.UniqueConstraint("slug", name=op.f("uq_tenants_slug")),
    )
    op.create_index(op.f("idx_tenants_slug"), "tenants", ["slug"], unique=False)

    # ── tenant_users ───────────────────────────────────────────────────────────
    op.create_table(
        "tenant_users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("pin_hash", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=True),
        sa.Column("totp_secret", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenant_users")),
    )
    op.create_index(
        op.f("idx_tenant_users_tenant_id"), "tenant_users", ["tenant_id"], unique=False
    )
    op.create_index(
        "idx_tenant_users_email", "tenant_users", ["email"], unique=False
    )

    # ── audit_logs ─────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(
        op.f("idx_audit_logs_tenant_id"), "audit_logs", ["tenant_id"], unique=False
    )
    op.create_index(
        op.f("idx_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False
    )

    # ── audit_logs append-only trigger ─────────────────────────────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'audit_logs are append-only: % on % is forbidden',
                TG_OP, TG_TABLE_NAME;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER audit_logs_no_update_delete
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();
    """)


def downgrade() -> None:
    # Drop trigger + function before tables
    op.execute(
        "DROP TRIGGER IF EXISTS audit_logs_no_update_delete ON audit_logs;"
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_modification;")

    # Drop in reverse FK dependency order
    op.drop_index(op.f("idx_audit_logs_actor_id"), table_name="audit_logs")
    op.drop_index(op.f("idx_audit_logs_tenant_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("idx_tenant_users_email", table_name="tenant_users")
    op.drop_index(
        op.f("idx_tenant_users_tenant_id"), table_name="tenant_users"
    )
    op.drop_table("tenant_users")

    op.drop_index(op.f("idx_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")
