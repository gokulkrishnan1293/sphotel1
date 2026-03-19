"""fix report tenant_id columns from uuid to varchar

Revision ID: 0026
Revises: 0025
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = '0026'
down_revision = '0025'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('fixed_report_configs', 'tenant_id',
                    type_=sa.String(),
                    existing_type=sa.UUID(),
                    postgresql_using='tenant_id::text')
    op.alter_column('custom_reports', 'tenant_id',
                    type_=sa.String(),
                    existing_type=sa.UUID(),
                    postgresql_using='tenant_id::text')


def downgrade() -> None:
    op.alter_column('fixed_report_configs', 'tenant_id',
                    type_=sa.UUID(),
                    existing_type=sa.String(),
                    postgresql_using='tenant_id::uuid')
    op.alter_column('custom_reports', 'tenant_id',
                    type_=sa.UUID(),
                    existing_type=sa.String(),
                    postgresql_using='tenant_id::uuid')
