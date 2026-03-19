"""Add short_code to tenant_users."""
import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenant_users", sa.Column("short_code", sa.Integer(), nullable=True))
    op.create_unique_constraint("uq_tenant_users_short_code", "tenant_users", ["tenant_id", "short_code"])


def downgrade() -> None:
    op.drop_constraint("uq_tenant_users_short_code", "tenant_users", type_="unique")
    op.drop_column("tenant_users", "short_code")
