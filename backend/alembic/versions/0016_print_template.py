"""Add print_template JSONB to tenants table."""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None

_DEFAULT: dict = {
    "restaurant_name": "",
    "address_line_1": "",
    "address_line_2": "",
    "phone": "",
    "gst_number": "",
    "fssai_number": "",
    "footer_message": "Thanks",
    "show_name_field": True,
    "show_cashier": True,
    "show_token_no": True,
    "show_bill_no": True,
    "receipt_width": 42,
    "kot_width": 32,
}


def upgrade() -> None:
    import json

    op.add_column(
        "tenants",
        sa.Column(
            "print_template",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text(f"'{json.dumps(_DEFAULT)}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "print_template")
