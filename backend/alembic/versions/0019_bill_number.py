"""Add auto-incrementing bill_number to bills."""
import sqlalchemy as sa
from alembic import op

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS bills_bill_number_seq START 1001")
    op.add_column(
        "bills",
        sa.Column(
            "bill_number",
            sa.Integer(),
            server_default=sa.text("nextval('bills_bill_number_seq')"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("bills", "bill_number")
    op.execute("DROP SEQUENCE IF EXISTS bills_bill_number_seq")
