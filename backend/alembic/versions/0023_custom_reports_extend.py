"""Extend custom_reports with dimension and days for dynamic query builder."""
import sqlalchemy as sa
from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("custom_reports", sa.Column("dimension", sa.String(), nullable=True))
    op.add_column("custom_reports", sa.Column("days", sa.Integer(), server_default="7", nullable=False))


def downgrade() -> None:
    op.drop_column("custom_reports", "days")
    op.drop_column("custom_reports", "dimension")
