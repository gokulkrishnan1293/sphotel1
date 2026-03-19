"""Add bill_close_ux feature flag."""
import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tenant_feature_flags",
        sa.Column("bill_close_ux", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("tenant_feature_flags", "bill_close_ux")
