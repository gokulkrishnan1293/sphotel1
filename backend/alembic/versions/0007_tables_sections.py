"""create sections and table_layouts tables

Revision ID: 0007
Revises: 0006
Create Date: 2026-03-18
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS sections (
            id          UUID        NOT NULL DEFAULT gen_random_uuid(),
            tenant_id   VARCHAR     NOT NULL,
            name        VARCHAR     NOT NULL,
            color       VARCHAR(7)  NOT NULL DEFAULT '#3b82f6',
            position    INTEGER     NOT NULL DEFAULT 0,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_sections PRIMARY KEY (id),
            CONSTRAINT fk_sections_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_sections_tenant_id ON sections (tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS table_layouts (
            id          UUID        NOT NULL DEFAULT gen_random_uuid(),
            tenant_id   VARCHAR     NOT NULL,
            section_id  UUID        NOT NULL,
            name        VARCHAR     NOT NULL,
            capacity    INTEGER     NOT NULL DEFAULT 4,
            is_active   BOOLEAN     NOT NULL DEFAULT true,
            position    INTEGER     NOT NULL DEFAULT 0,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT pk_table_layouts PRIMARY KEY (id),
            CONSTRAINT fk_table_layouts_tenant_id_tenants
                FOREIGN KEY (tenant_id) REFERENCES tenants (slug) ON DELETE CASCADE,
            CONSTRAINT fk_table_layouts_section_id_sections
                FOREIGN KEY (section_id) REFERENCES sections (id) ON DELETE CASCADE
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_table_layouts_tenant_id ON table_layouts (tenant_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_table_layouts_section_id ON table_layouts (section_id)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_table_layouts_section_id")
    op.execute("DROP INDEX IF EXISTS idx_table_layouts_tenant_id")
    op.execute("DROP TABLE IF EXISTS table_layouts")
    op.execute("DROP INDEX IF EXISTS idx_sections_tenant_id")
    op.execute("DROP TABLE IF EXISTS sections")
