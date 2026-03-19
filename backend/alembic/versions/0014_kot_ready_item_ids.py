"""Add ready_item_ids JSONB to kot_tickets."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "kot_tickets",
        sa.Column("ready_item_ids", postgresql.JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("kot_tickets", "ready_item_ids")
