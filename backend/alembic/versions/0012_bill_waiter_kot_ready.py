"""Add waiter_id to bills, ready_at to kot_tickets."""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bills", sa.Column("waiter_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_bills_waiter_id", "bills", "tenant_users", ["waiter_id"], ["id"], ondelete="SET NULL"
    )
    op.add_column("kot_tickets", sa.Column("ready_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_constraint("fk_bills_waiter_id", "bills", type_="foreignkey")
    op.drop_column("bills", "waiter_id")
    op.drop_column("kot_tickets", "ready_at")
