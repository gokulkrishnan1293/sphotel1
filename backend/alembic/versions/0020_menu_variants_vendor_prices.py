"""Normalize menu variants to table; add vendor prices table."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old columns — no production data to preserve
    op.drop_column("menu_items", "variants")
    op.drop_column("menu_items", "online_price_paise")

    op.create_table(
        "menu_item_variants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("menu_item_id", UUID(as_uuid=True), sa.ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parcel_price_paise", sa.Integer(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_menu_item_variants_item_id", "menu_item_variants", ["menu_item_id"])

    op.create_table(
        "menu_item_vendor_prices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("menu_item_id", UUID(as_uuid=True), sa.ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=True),
        sa.Column("variant_id", UUID(as_uuid=True), sa.ForeignKey("menu_item_variants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("vendor_slug", sa.String(50), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
    )
    op.create_index("idx_vendor_prices_item", "menu_item_vendor_prices", ["menu_item_id"])
    op.create_index("idx_vendor_prices_variant", "menu_item_vendor_prices", ["variant_id"])
    op.create_unique_constraint("uq_vendor_price_item", "menu_item_vendor_prices", ["menu_item_id", "vendor_slug"])
    op.create_unique_constraint("uq_vendor_price_variant", "menu_item_vendor_prices", ["variant_id", "vendor_slug"])


def downgrade() -> None:
    op.drop_table("menu_item_vendor_prices")
    op.drop_table("menu_item_variants")
    op.add_column("menu_items", sa.Column("variants", JSONB(), nullable=True))
    op.add_column("menu_items", sa.Column("online_price_paise", sa.Integer(), nullable=True))
