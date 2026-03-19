"""Create custom_reports table."""
import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_reports",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("metric", sa.String(), nullable=False),
        sa.Column("chart_type", sa.String(), nullable=False, server_default="bar"),
        sa.Column("telegram_schedule", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_custom_reports"),
    )
    op.create_index("idx_custom_reports_tenant_id", "custom_reports", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("idx_custom_reports_tenant_id", table_name="custom_reports")
    op.drop_table("custom_reports")
