"""Add keyboard_shortcuts to tenants."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("keyboard_shortcuts", JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "keyboard_shortcuts")
