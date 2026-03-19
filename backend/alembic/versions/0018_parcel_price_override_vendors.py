"""Add parcel_price to menu items/variants, override_price to bill items, online_vendors to tenants."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("menu_items", sa.Column("parcel_price_paise", sa.Integer(), nullable=True))
    op.add_column("bill_items", sa.Column("override_price_paise", sa.Integer(), nullable=True))
    op.add_column("tenants", sa.Column("online_vendors", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "online_vendors")
    op.drop_column("bill_items", "override_price_paise")
    op.drop_column("menu_items", "parcel_price_paise")
