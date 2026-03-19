"""Create print_jobs table."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "print_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.String, nullable=False),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("bills.id", ondelete="SET NULL"), nullable=True),
        sa.Column("job_type", sa.String, nullable=False),       # receipt | kot
        sa.Column("status", sa.String, nullable=False, server_default="pending"),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("printer_name", sa.String, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_print_jobs_tenant_status", "print_jobs", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_index("idx_print_jobs_tenant_status", table_name="print_jobs")
    op.drop_table("print_jobs")
