"""create bills and kot_tickets tables

Revision ID: 0008
Revises: 0007
Create Date: 2026-03-18
"""

from typing import Sequence, Union
from alembic import op

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for ddl in [
        "DO $$ BEGIN CREATE TYPE bill_type AS ENUM ('table','parcel','online'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE bill_status AS ENUM ('draft','kot_sent','partially_sent','billed','void'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
        "DO $$ BEGIN CREATE TYPE payment_method AS ENUM ('cash','card','upi','wallet','other'); EXCEPTION WHEN duplicate_object THEN NULL; END $$",
    ]:
        op.execute(ddl)

    op.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id              UUID            NOT NULL DEFAULT gen_random_uuid(),
            tenant_id       VARCHAR         NOT NULL,
            bill_type       bill_type       NOT NULL,
            status          bill_status     NOT NULL DEFAULT 'draft',
            table_id        UUID,
            covers          INTEGER,
            reference_no    VARCHAR,
            platform        VARCHAR(50),
            subtotal_paise  INTEGER         NOT NULL DEFAULT 0,
            discount_paise  INTEGER         NOT NULL DEFAULT 0,
            gst_paise       INTEGER         NOT NULL DEFAULT 0,
            total_paise     INTEGER         NOT NULL DEFAULT 0,
            payment_method  payment_method,
            paid_at         TIMESTAMPTZ,
            notes           TEXT,
            created_by      UUID            NOT NULL,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
            CONSTRAINT pk_bills PRIMARY KEY (id),
            CONSTRAINT fk_bills_tenant_id_tenants FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE,
            CONSTRAINT fk_bills_table_id_table_layouts FOREIGN KEY (table_id) REFERENCES table_layouts (id) ON DELETE SET NULL,
            CONSTRAINT fk_bills_created_by_tenant_users FOREIGN KEY (created_by) REFERENCES tenant_users (id) ON DELETE RESTRICT
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_bills_tenant_id ON bills (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bills_tenant_status ON bills (tenant_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_bills_table_id ON bills (table_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS kot_tickets (
            id              UUID        NOT NULL DEFAULT gen_random_uuid(),
            tenant_id       VARCHAR     NOT NULL,
            bill_id         UUID        NOT NULL,
            ticket_number   INTEGER     NOT NULL,
            fired_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_kot_tickets PRIMARY KEY (id),
            CONSTRAINT fk_kot_tickets_tenant_id_tenants FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE,
            CONSTRAINT fk_kot_tickets_bill_id_bills FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_kot_tickets_tenant_id ON kot_tickets (tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_kot_tickets_bill_id ON kot_tickets (bill_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_kot_tickets_bill_id")
    op.execute("DROP INDEX IF EXISTS idx_kot_tickets_tenant_id")
    op.execute("DROP TABLE IF EXISTS kot_tickets")
    op.execute("DROP INDEX IF EXISTS idx_bills_table_id")
    op.execute("DROP INDEX IF EXISTS idx_bills_tenant_status")
    op.execute("DROP INDEX IF EXISTS idx_bills_tenant_id")
    op.execute("DROP TABLE IF EXISTS bills")
    op.execute("DROP TYPE IF EXISTS payment_method")
    op.execute("DROP TYPE IF EXISTS bill_status")
    op.execute("DROP TYPE IF EXISTS bill_type")
