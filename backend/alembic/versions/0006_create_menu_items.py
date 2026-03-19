"""create menu_items table

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-18
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create food_type enum — use DO block to tolerate partial prior runs
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE food_type AS ENUM ('veg', 'egg', 'non_veg');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id          UUID        NOT NULL DEFAULT gen_random_uuid(),
            tenant_id   VARCHAR     NOT NULL,
            name        VARCHAR     NOT NULL,
            category    VARCHAR     NOT NULL,
            short_code  INTEGER,
            price_paise INTEGER     NOT NULL DEFAULT 0,
            food_type   food_type   NOT NULL DEFAULT 'veg',
            description TEXT,
            is_available BOOLEAN    NOT NULL DEFAULT true,
            display_order INTEGER   NOT NULL DEFAULT 0,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_menu_items PRIMARY KEY (id),
            CONSTRAINT fk_menu_items_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE,
            CONSTRAINT uq_menu_items_tenant_short_code
                UNIQUE (tenant_id, short_code) DEFERRABLE INITIALLY DEFERRED
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_menu_items_tenant_id
        ON menu_items (tenant_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_menu_items_tenant_category
        ON menu_items (tenant_id, category)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_menu_items_tenant_category")
    op.execute("DROP INDEX IF EXISTS idx_menu_items_tenant_id")
    op.execute("DROP TABLE IF EXISTS menu_items")
    op.execute("DROP TYPE IF EXISTS food_type")
