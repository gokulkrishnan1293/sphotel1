"""add user_role enum type to tenant_users

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-18

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the PostgreSQL ENUM type
    op.execute("""
        CREATE TYPE user_role AS ENUM (
            'biller', 'waiter', 'kitchen_staff',
            'manager', 'admin', 'super_admin'
        )
    """)
    # Alter existing VARCHAR column to use the new enum type.
    # USING clause casts existing string values — any invalid value fails the migration.
    op.execute("""
        ALTER TABLE tenant_users
        ALTER COLUMN role TYPE user_role
        USING role::user_role
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE tenant_users
        ALTER COLUMN role TYPE VARCHAR
        USING role::text
    """)
    op.execute("DROP TYPE IF EXISTS user_role")
