"""Create print_agents table for per-agent authentication."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "print_agents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", sa.String, nullable=False, index=True),
        sa.Column("name", sa.String, nullable=False),
        # one-time registration token hash (cleared after activation)
        sa.Column("registration_token_hash", sa.String, nullable=True),
        sa.Column("registration_token_expires_at", sa.DateTime(timezone=True), nullable=True),
        # permanent api key hash written after activation
        sa.Column("api_key_hash", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=False, server_default="offline"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        # JSONB config: { "printer_type": "network|usb|file", "host": ..., "port": ... }
        sa.Column("printer_config", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_print_agents_tenant", "print_agents", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("idx_print_agents_tenant", table_name="print_agents")
    op.drop_table("print_agents")
