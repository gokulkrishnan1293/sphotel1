"""Add printer_role to print_agents and target_role to print_jobs."""
import sqlalchemy as sa
from alembic import op

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("print_agents", sa.Column("printer_role", sa.String(),
                  server_default="main", nullable=False))
    op.add_column("print_jobs", sa.Column("target_role", sa.String(),
                  server_default="main", nullable=False))


def downgrade() -> None:
    op.drop_column("print_agents", "printer_role")
    op.drop_column("print_jobs", "target_role")
