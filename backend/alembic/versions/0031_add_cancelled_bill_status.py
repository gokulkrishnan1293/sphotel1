"""Add cancelled value to bill_status enum."""
from alembic import op

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE bill_status ADD VALUE IF NOT EXISTS 'cancelled'")


def downgrade() -> None:
    pass  # PostgreSQL cannot remove enum values
