"""Make bill_number nullable — assigned lazily on KOT fire or bill close."""
import sqlalchemy as sa
from alembic import op

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("bills", "bill_number", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.execute("UPDATE bills SET bill_number = 0 WHERE bill_number IS NULL")
    op.alter_column("bills", "bill_number", existing_type=sa.Integer(), nullable=False)
