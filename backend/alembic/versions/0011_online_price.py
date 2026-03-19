"""Add online_price_paise to menu_items."""
import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("menu_items", sa.Column("online_price_paise", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("menu_items", "online_price_paise")
