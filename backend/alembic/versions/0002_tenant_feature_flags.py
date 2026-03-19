"""add tenant_feature_flags table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-17

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenant_feature_flags",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "waiter_mode", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "suggestion_engine", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "telegram_alerts", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "gst_module", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "payroll_rewards", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "discount_complimentary",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "waiter_transfer", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name=op.f("fk_tenant_feature_flags_tenant_id_tenants"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id", name=op.f("pk_tenant_feature_flags")
        ),
    )


def downgrade() -> None:
    op.drop_table("tenant_feature_flags")
