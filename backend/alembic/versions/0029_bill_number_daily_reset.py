"""Change bill_number from sequence to daily-reset counter (like KOT ticket_number)."""
import sqlalchemy as sa
from alembic import op

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove the sequence default — bill_number will now be set by application code
    op.alter_column("bills", "bill_number", server_default=None)
    op.execute("DROP SEQUENCE IF EXISTS bills_bill_number_seq")


def downgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS bills_bill_number_seq START 1001")
    op.alter_column(
        "bills",
        "bill_number",
        server_default=sa.text("nextval('bills_bill_number_seq')"),
    )
