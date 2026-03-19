import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# CRITICAL: Import ALL models here so autogenerate detects them.
# Without this, `alembic revision --autogenerate` produces empty migrations.
# Add new model imports here as each story creates new models.
from app.models import base as _base  # noqa: F401 — registers Base.metadata
from app.models import tenant as _tenant  # noqa: F401
from app.models import user as _user  # noqa: F401
from app.models import audit_log as _audit_log  # noqa: F401
from app.models import menu as _menu  # noqa: F401

from app.models.base import Base

target_metadata = Base.metadata


def run_migrations_online() -> None:
    engine = create_async_engine(settings.DATABASE_URL)

    def _run(conn: object) -> None:
        context.configure(
            connection=conn,  # type: ignore[arg-type]
            target_metadata=target_metadata,
            transaction_per_migration=True,
        )
        context.run_migrations()

    async def do_run() -> None:
        async with engine.connect() as connection:
            await connection.run_sync(_run)

    asyncio.run(do_run())


run_migrations_online()
