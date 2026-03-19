"""create bill_items table and item_status enum

Revision ID: 0009
Revises: 0008
Create Date: 2026-03-18
"""

from typing import Sequence, Union
from alembic import op

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE item_status AS ENUM ('pending', 'sent', 'voided');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id              UUID        NOT NULL DEFAULT gen_random_uuid(),
            tenant_id       VARCHAR     NOT NULL,
            bill_id         UUID        NOT NULL,
            menu_item_id    UUID,
            name            VARCHAR     NOT NULL,
            category        VARCHAR     NOT NULL,
            price_paise     INTEGER     NOT NULL,
            food_type       food_type   NOT NULL DEFAULT 'veg',
            quantity        INTEGER     NOT NULL DEFAULT 1,
            status          item_status NOT NULL DEFAULT 'pending',
            kot_ticket_id   UUID,
            notes           TEXT,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_bill_items PRIMARY KEY (id),
            CONSTRAINT fk_bill_items_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE,
            CONSTRAINT fk_bill_items_bill_id_bills
                FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE,
            CONSTRAINT fk_bill_items_menu_item_id_menu_items
                FOREIGN KEY (menu_item_id) REFERENCES menu_items (id) ON DELETE SET NULL,
            CONSTRAINT fk_bill_items_kot_ticket_id_kot_tickets
                FOREIGN KEY (kot_ticket_id) REFERENCES kot_tickets (id) ON DELETE SET NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items (bill_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bill_items_tenant_id ON bill_items (tenant_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_bill_items_tenant_id")
    op.execute("DROP INDEX IF EXISTS idx_bill_items_bill_id")
    op.execute("DROP TABLE IF EXISTS bill_items")
    op.execute("DROP TYPE IF EXISTS item_status")
