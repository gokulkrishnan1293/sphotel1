"""Add telegram_bot_token and telegram_chat_id to tenants."""
import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("telegram_bot_token", sa.String(), nullable=True))
    op.add_column("tenants", sa.Column("telegram_chat_id", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "telegram_chat_id")
    op.drop_column("tenants", "telegram_bot_token")
